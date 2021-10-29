###################
mkname Requirements
###################

The purpose of this document is to detail the requirements for the
mkname package. This is an initial take to help with planning. There
may be additional requirements or non-required features added in the
future.


Purpose
-------
The purposes of mkname are:

*   Be able to generate a randomized name for a person that seems
    vaguely plausible within the developer's cultural context
    (Midwestern United States)
*   Allow the ability to add new base names to use as building blocks
    for the created names without having to hard code them.


Functional Requirements
-----------------------
The following are the functional requirements for mkname:

1.  mkname can generate a given name.
2.  mkname can generate a family name.
3.  mkname can use a database of seed names as parts to create a
    randomized name.
4.  mkname can update the name seed database with new names.
5.  mkname can be used from the command line.
6.  mkname can be imported and used within other Python applications.
7.  mkname can have different sets of seed names to change the
    character of the generated names.

The following are not strictly requirements, but are features that
would be good to add in the future to allow the package to be useful
outside of the developer's limited cultural context.

1.  mkname can generate names that vaguely adhere cultural contexts
    beyond the developer's.
2.  mkname can use a database of undesirable names to avoid the
    creation of names that would lead to undesired reactions or
    results. (Preventing this algorithmically seems unlikely to be
    possible.)


Technical Requirements
----------------------
The following are the technical requirements for mkname:

1.  mkname will be written in Python.
2.  mkname will not hardcode seed names for use in name generation,
    but can come with an initial set of names to initialize the
    database.
