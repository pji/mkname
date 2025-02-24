"""
lm
~~

Tools for creating a language model for names.

Problems to solve:

*   Store the trained model.
*   Reuse a stored model.
*   Generate for specific types, cultures, dates, and genders.
*   Separate the training code out into its own module.
*   Include models trained at the character and the syllable level.

.. note::
    What I'm doing here is ridiculous. I'm using a technique known
    for training on large amounts of text and generating large amounts
    of text to specifically generate names, which are short. Based on
    initial testing, this will probably limit how much the output
    will deviate from the training data. That's probably OK for what
    I'm doing here, but it does raise the question whether it's
    worth the work put into it.

    If the model just generates the same data I could get from a
    random pick from the database, what is the benefit of the LM
    over the database? The answer here will probably be "not much".
    Though, it could provide some about of space savings, if the
    model is smaller than the database.

    Still, it's worth doing for the exercise. If nothing else, it
    got me to look closer at :mod:`pytorch`, which could help me
    move some processing over to the GPUs in :mod:`pjimg`. It also
    serves as a start with thinking about how to use these techniques
    in developing solutions rather than just thinking about LLMs
    as the output you can get from the ChatGPT.
"""
from argparse import ArgumentParser
from collections import OrderedDict
from collections.abc import Callable
from datetime import datetime
from functools import partial
from pathlib import Path
from random import shuffle
from typing import Callable, Sequence

import torch
import torch.nn as nn
from torch.nn import functional as F

from mkname.db import get_names
from mkname.model import Name
from mkname.utility import split_into_syllables


# Constants.
DEFAULT_PATH = 'all_names.pt'
DEVICE = 'mps' if torch.backends.mps.is_available() else 'cpu'
DROPOUT = 0.2
LEARNING_RATE = 3e-4
NUM_EMBEDDED_DIMS = 384
NUM_HEADS = 6
NUM_LAYERS = 6

# The number of blocks to use in a training iteration.
BATCH_SIZE = 16

# The number of tokens in the original data in a block of training data.
# With the move to training on single names, this is no longer used.
# BLOCK_SIZE = 64

# How often to display training stats during a run.
# EVAL_INTERVAL = 500
EVAL_INTERVAL = 50

# The number of iterations when estimating loss during training.
# EVAL_ITERATIONS = 200
EVAL_ITERATIONS = 20

# The number of iterations during a training run.
# MAX_ITERATIONS = 5_000
# MAX_ITERATIONS = 1_000
# MAX_ITERATIONS = 250
MAX_ITERATIONS = 100


# Types.
EncodeMap = dict[str, int]
DecodeMap = dict[int, str]


# Classes for the model.
class BigramLanguageModel(nn.Module):
    """A language model.

    :param vocab_size:
    :param num_dims:
    :param block_size:
    :param num_heads:
    :param num_layers:
    :returns: A :class:`mkname.lm.BigramLanguageModel` object.
    :rtype: mkname.lm.BigramLanguageModel
    """
    def __init__(
        self, vocab_size: int,
        emap: EncodeMap,
        dmap: DecodeMap,
        maxlen: int = 10,
        num_dims: int = NUM_EMBEDDED_DIMS,
        block_size: int = 10,
        num_heads: int = NUM_HEADS,
        num_layers: int = NUM_LAYERS
    ) -> None:
        super().__init__()
        self.vocab_size = vocab_size
        self.emap = emap
        self.dmap = dmap
        self.maxlen = maxlen
        self.num_dims = num_dims
        self.block_size = block_size
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.init()

    def init(self) -> None:
        # Each token directly reads off the logits for the next token
        # from a lookup table.
        self.token_embedding_table = nn.Embedding(
            self.vocab_size,
            self.num_dims
        )
        self.position_embedding_table = nn.Embedding(
            self.block_size,
            self.num_dims
        )
        self.blocks = nn.Sequential(*[
            Block(self.num_dims, self.num_heads, block_size=self.block_size)
            for _ in range(self.num_layers)
        ])
        self.ln_f = nn.LayerNorm(self.num_dims)
        self.lm_head = nn.Linear(self.num_dims, self.vocab_size)

    def forward(
        self, idx: torch.Tensor,
        targets: torch.Tensor = None
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        b, t = idx.shape

        token_embeddings = self.token_embedding_table(idx)
        pos_embeddings = self.position_embedding_table(
            torch.arange(t, device=DEVICE)
        )
        x = token_embeddings + pos_embeddings
        x = self.blocks(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)

        if targets is None:
            loss = None

        # To determine the quality of the guesses, you need to rearrange
        # the embedding table to match cross_entropy's expectations.
        else:
            b, t, c = logits.shape
            logits = logits.view(b*t, c)
            targets = targets.view(b*t)
            loss = F.cross_entropy(logits, targets)

        return logits, loss

    def generate(
        self, idx: torch.Tensor,
        max_new_tokens: int
    ) -> torch.Tensor:
        # idx is (B, T) array of indices in current context.
        for _ in range(max_new_tokens):
            # Crop index to the last block size tokens.
            idx_cond = idx[:, -self.block_size:]

            # Get the predictions.
            logits, _ = self(idx_cond)

            # Focus only on the last time step.
            logits = logits[:, -1, :]

            # Apply softmax to get the probabilities.
            probs = F.softmax(logits, dim=-1)

            # Sample from the distribution.
            idx_next = torch.multinomial(probs, num_samples=1)

            # Append sampled index to the running sequence.
            idx = torch.cat((idx, idx_next), dim=1)
        return idx

    def get_extra_state(self):
        return {
            'vocab_size': self.vocab_size,
            'emap': self.emap,
            'dmap': self.dmap,
            'maxlen': self.maxlen,
            'num_dims': self.num_dims,
            'block_size': self.block_size,
            'num_heads': self.num_heads,
            'num_layers': self.num_layers,
        }

    def set_extra_state(self, state):
        self.vocab_size = state['vocab_size']
        self.emap = state['emap']
        self.dmap = state['dmap']
        self.maxlen = state['maxlen']
        self.num_dims = state['num_dims']
        self.block_size = state['block_size']
        self.num_heads = state['num_heads']
        self.num_layers = state['num_layers']
        self.init()


class Block(nn.Module):
    """Transformer block: communication followed by computation."""
    def __init__(
        self,
        num_dims: int,
        num_heads: int,
        block_size: int = 10
    ) -> None:
        super().__init__()
        head_size = num_dims // num_heads
        self.sa = MultiHeadAttention(
            num_heads,
            head_size,
            num_dims,
            block_size=block_size
        )
        self.ffwd = FeedForward(num_dims)
        self.ln1 = nn.LayerNorm(num_dims)
        self.ln2 = nn.LayerNorm(num_dims)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.sa(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))
        return x


class FeedForward(nn.Module):
    """A simple linear layer followed by a non-linearity."""
    def __init__(self, num_dims: int, dropout: float = DROPOUT) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(num_dims, 4 * num_dims),
            nn.ReLU(),

            # Projection layer.
            nn.Linear(4 * num_dims, num_dims),

            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class Head(nn.Module):
    """One head of self-attention."""
    def __init__(
        self, head_size: int,
        num_dims: int = NUM_EMBEDDED_DIMS,
        block_size: int = 10,
        dropout: float = DROPOUT
    ) -> None:
        super().__init__()
        self.key = nn.Linear(num_dims, head_size, bias=False)
        self.query = nn.Linear(num_dims, head_size, bias=False)
        self.value = nn.Linear(num_dims, head_size, bias=False)
        self.register_buffer('tril', torch.tril(torch.ones(
            block_size,
            block_size
        )))
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, t, c = x.shape
        k = self.key(x)
        q = self.query(x)

        # Compute affinities.
        weight = q @ k.transpose(-2, -1) * c ** -0.5
        weight = weight.masked_fill(self.tril[:t, :t] == 0, float('-inf'))
        weight = F.softmax(weight, dim=-1)
        weight = self.dropout(weight)

        # Perform the weighted aggregation of the values.
        v = self.value(x)
        out = weight @ v
        return out


class MultiHeadAttention(nn.Module):
    """Multiple heads of self-attention in parallel."""
    def __init__(
        self, num_heads: int,
        head_size: int,
        num_dims: int,
        dropout: float = DROPOUT,
        block_size: int = 10
    ) -> None:
        super().__init__()
        self.heads = nn.ModuleList(
            [Head(head_size, block_size=block_size) for _ in range(num_heads)]
        )
        self.projection = nn.Linear(num_dims, num_dims)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        out = self.projection(out)
        out = self.dropout(out)
        return out


# Utility functions.
def decode(decode_map: dict[int, str], tokens:Sequence[int]) -> str:
    return ''.join(decode_map[n] for n in tokens)


def encode(encode_map: dict[str, int], text: Sequence[str]) -> tuple[int]:
    return tuple(encode_map[c] for c in text)


# Training functions.
def _char_tokenizer(text: str) -> list[str]:
    """Tokenize at the individual character level."""
    return [c for c in text]


def _syllable_tokenizer(text: str) -> list[str]:
    """Tokenize at the syllable level."""
    tokens = []
    syllables = split_into_syllables(text)
    for syllable in syllables:
        tokens.append(syllable)
    return tokens


def build_token_maps(text: list[str]) -> tuple[EncodeMap, DecodeMap]:
    """Create the token maps from the given text.

    :param text: The training text.
    :returns: A :class:`tuple` object with the encode and decode maps.
    :rtype: tuple
    """
    # Create the tokens for the model. The model itself just works
    # with integers. The tokens are needed to translate those ints
    # back and forth into text.
    tokens = sorted(list(set(text)))

    # The encoding map is used to translate the characters from the
    # training data into the intergers the model uses.
    encode_map = {char: n for n, char in enumerate(tokens)}

    # The decoding map is used to translate the integers the model
    # outputs into their associated characters.
    decode_map = {n: char for n, char in enumerate(tokens)}

    # Return the token maps.
    return encode_map, decode_map


def build_tensor(
    encode: Callable[[Sequence[str],], tuple[int]],
    text: str
) -> torch.Tensor:
    encoded = encode(text)
    return torch.tensor(encoded, dtype=torch.long)


@torch.no_grad()
def estimate_loss(
    m: BigramLanguageModel,
    training_data: torch.Tensor,
    validation_data: torch.Tensor,
    eval_iterations: int =EVAL_ITERATIONS
) -> dict[str, torch.Tensor]:
    """Estimate the loss during a training run.

    "Loss" for an LLM is the distance between the model's predictions
    and actual output. Essentially, it measures how good the model is
    at producing data that meets expectations.

    :param m: The model being trained.
    :param training_data: The part of the original data used for
        training the model.
    :param validation_data: The part of the original data used for
        validating the model's predictions.
    :param eval_iterations: The number of predictions to evaluate.
    :returns: A :class:`dict` object containing the loss evaluations.
    :rtype: dict
    """
    out = {}
    m.eval()
    for name, data in [('train', training_data), ('val', validation_data)]:
        losses = torch.zeros(eval_iterations)
        for k in range(eval_iterations):
#             x, y = get_batch(data)
            x, y = get_name_batch(data)
            logits, loss = m(x, y)
            losses[k] = loss.item()
        out[name] = losses.mean()
    m.train()
    return out


def gather_training_data(
    tokenizer: Callable[[str,], str]
) -> tuple[EncodeMap, DecodeMap, torch.Tensor, int]:
    # Get the names.
    names = get_names()

    # Build the token maps.
    tokenized_names, maxlen = tokenize_names(names, tokenizer)
    all_tokens = set()
    for name in tokenized_names:
        for token in name:
            all_tokens.add(token)
    emap = {token: n for n, token in enumerate(all_tokens)}
    dmap = {n: token for n, token in enumerate(all_tokens)}

    # Create the data tensor.
    encoded = tuple(encode(emap, name) for name in tokenized_names)
    tensor = torch.tensor(encoded, dtype=torch.long)

    # Return the results.
    return emap, dmap, tensor, maxlen


def get_name_batch(
    data: torch.Tensor,
    batch_size: int = BATCH_SIZE
) -> tuple[torch.Tensor, torch.Tensor]:
    ix = torch.randint(len(data), (batch_size,))
    x = torch.stack([data[i, :-1] for i in ix])
    y = torch.stack([data[i, 1:] for i in ix])
    x, y = x.to(DEVICE), y.to(DEVICE)
    return x, y


def get_training_names() -> str:
    names = list(get_names())
    shuffle(names)
    return '\n'.join(name.name for name in names)


def split_data_for_validation(
    tensor: torch.Tensor,
    amount: float = 0.9
) -> tuple[torch.Tensor, torch.Tensor]:
    n = int(amount * len(tensor))
    training_data = tensor[:n]
    validation_data = tensor[n:]
    return training_data, validation_data


def tokenize_names(
    names: Sequence[Name],
    tokenizer: Callable[[str,], str]
) -> tuple[list[list[str]], int]:
    texts = [name.name for name in names]
    tokenized = [tokenizer(name) for name in texts]
    tokenized = [['\x02', *name] for name in tokenized]
    maxlen = max(len(name) for name in tokenized)
    for name in tokenized:
        while len(name) < maxlen:
            name.append('')
    return tokenized, maxlen


def train(
    tokenizer: Callable[[str,], str],
    steps: int = MAX_ITERATIONS,
    eval_interval: int = EVAL_INTERVAL,
    eval_iterations: int = EVAL_ITERATIONS,
    batch_size: int = BATCH_SIZE
) -> BigramLanguageModel:
    # Build the initial data and tokenization.
    emap, dmap, tensor, maxlen = gather_training_data(tokenizer)

    # Divvy into training and validation data.
    training_data, validation_data = split_data_for_validation(tensor)

    # Create the model.
    vocab_size = len(emap)
    model = BigramLanguageModel(
        vocab_size,
        emap,
        dmap,
        block_size=maxlen
    )
    m = model.to(DEVICE)
    optimizer = torch.optim.Adam(m.parameters(), lr=LEARNING_RATE)

    # Train the model.
    print('Starting training.')
    t0 = datetime.now()
    logits, loss = train_model(
        m,
        optimizer,
        training_data,
        validation_data,
        steps=steps,
        eval_interval=eval_interval,
        eval_iterations=eval_iterations,
        batch_size=BATCH_SIZE,
        t0=t0
    )
    duration = datetime.now() - t0
    print(f'Final training loss: {loss.item()}')
    print(f'Training duration: {duration}')
    print()

    # Return the model.
    return m


def train_model(
    m: BigramLanguageModel,
    optimizer: torch.optim.Adam,
    training_data: torch.Tensor,
    validation_data: torch.Tensor,
    steps: int = MAX_ITERATIONS,
    eval_interval: int = EVAL_INTERVAL,
    eval_iterations: int = EVAL_ITERATIONS,
    block_size: int = 10,
    batch_size: int = BATCH_SIZE,
    t0: datetime = datetime.now()
) -> tuple[torch.Tensor, torch.Tensor | None]:
    for i in range(steps):
        # Periodically evaluate the loss.
        if i % eval_interval == 0:
            losses = estimate_loss(
                m,
                training_data,
                validation_data,
                eval_iterations
            )
            print(
                f'{datetime.now() - t0} '
                f'Step {i}: '
                f'train loss {losses["train"]:.4f}, '
                f'val loss {losses["val"]:.4f}'
            )

        # Sample data.
#         xb, yb = get_batch(training_data, block_size, batch_size)
        xb, yb = get_name_batch(training_data, batch_size)

        # Evaluate loss.
        logits, loss = m(xb, yb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
    return logits, loss


# Generation functions.
def generate(m: BigramLanguageModel) -> str:
    # Create the decoder.
    decode_ = partial(decode, m.dmap)

    # Generate text from the trained model.
    print('Starting text generation.')
    t0 = datetime.now()
    stx = m.emap['\x02']
    seed = torch.tensor([[stx,], [stx,]], dtype=torch.long, device=DEVICE)
    generated_tokens = get_tokens_from_model(
        m,
        seed=seed,
        num_tokens=m.maxlen
    )
    generated_text = decode_(generated_tokens)
    if generated_text[0] == '\x02':
        generated_text = generated_text[1:]
    duration = datetime.now() - t0
    print(f'Generation duration: {duration}')
    return generated_text


def get_tokens_from_model(
    m: BigramLanguageModel,
    seed: torch.Tensor | None = None,
    num_tokens: int = 10
) -> list[int]:
    if seed is None:
        seed = torch.zeros((1, 1), dtype=torch.long, device=DEVICE)
    generated_values = m.generate(seed, num_tokens)
    return generated_values[0].tolist()


# Command scripts.
def create_new_model(
    path: Path | str,
    tokenizer: Callable[[str,], str],
    steps: int = MAX_ITERATIONS,
    eval_interval: int = EVAL_INTERVAL,
    eval_iterations: int = EVAL_ITERATIONS,
    batch_size: int = BATCH_SIZE
) -> None:
    """Train a new model and store it for later use."""
    # Warn if the path exists.
    path = Path(path)
    if path.exists():
        answer = input('Path already exists. Continue? [y/N]')
        if answer.lower() not in ['y', 'yes']:
            exit()

    # Create the new model.
    m = train(
        tokenizer,
        steps,
        eval_interval=eval_interval,
        eval_iterations=eval_iterations,
        batch_size=BATCH_SIZE
    )

    # Serialize the model.
    m_state = m.state_dict()
    torch.save(m_state, path)


def generate_name(path: Path | str) -> None:
    """Load a model and generate a name."""
    # Make sure the model exists.
    path = Path(path)
    if not path.exists():
        msg = 'The model file does not exist.'
        print(msg)
        print()
        exit()

    # Load the model.
    m_state = torch.load(path)
    new_m = BigramLanguageModel(0, {}, {}, 0)
    new_m.load_state_dict(m_state)
    new_m.to(DEVICE)

    # Generate text from the trained model.
    name = generate(new_m)
    print()
    print(name)
    print()


# Parse a command line invocation.
def main() -> None:
    """Response to commands passed through the CLI.

    :returns: `None`.
    :rtype: NoneType
    """
    # Setup for configuration options.
    tokenizers = {
        'char': _char_tokenizer,
        'syllable': _syllable_tokenizer,
    }

    # Set up the command line interface.
    p = ArgumentParser(
        description='Work with the name generation neural network.',
        prog='mkname.lm',
    )
    p.add_argument(
        '--batch_size', '-b',
        help='The number of names used in a training iteration.',
        action='store',
        default=BATCH_SIZE,
        type=int
    )
    p.add_argument(
        '--eval_interval', '-e',
        help='How many training iterations between UI updates.',
        action='store',
        default=EVAL_INTERVAL,
        type=int
    )
    p.add_argument(
        '--iterations', '-i',
        help='Number of training iterations.',
        action='store',
        default=MAX_ITERATIONS,
        type=int
    )
    p.add_argument(
        '--eval_iterations', '-I',
        help='Number of evaluation iterations.',
        action='store',
        default=EVAL_ITERATIONS,
        type=int
    )
    p.add_argument(
        '--tokenizer', '-k',
        help='Tokenizer used when generating a new model.',
        action='store',
        choices=tokenizers.keys(),
        default='syllable'
    )
    p.add_argument(
        '--path', '-p',
        help='The path to the model.',
        action='store',
        default=DEFAULT_PATH,
        type=str,
    )
    p.add_argument(
        '--seed', '-s',
        help='Provide a seed to the random number generator.',
        action='store',
        type=int
    )
    p.add_argument(
        '--train_model', '-t',
        help='Train a new model.',
        action='store_true'
    )
    args = p.parse_args()

    # Configure the run.
    if args.seed:
        torch.manual_seed(args.seed)

    # Run the command script.
    if args.train_model:
        create_new_model(
            args.path,
            tokenizers[args.tokenizer],
            steps = args.iterations,
            eval_interval=args.eval_interval,
            eval_iterations=args.eval_iterations,
            batch_size=args.batch_size
        )
    else:
        generate_name(args.path)


if __name__ == '__main__':
    main()
