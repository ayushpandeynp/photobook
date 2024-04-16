## Database Schemas and Constraints

### Users Table

The users table stores registered users as well as visitors in the
Photobook database. It stores a ***user**\_**id*** which is a set as the
Primary Key for this table.

Another constraint in this table is the ***gender*** column. We only
allow 3 types of characters –'M', 'F', 'O' –as the value of this column.
This is ensured using the **CHECK **keyword. In case this check fails,
the database will return an error.

One interesting constraint we have on this table is demonstrated by the
following SQL:

```sql
CONSTRAINT chk_visitor CHECK (

(is_visitor AND fname IS NULL AND lname IS NULL AND email IS NULL AND dob IS NULL AND hometown IS NULL AND gender IS NULL AND password IS NULL)
    
    OR
        
(NOT is_visitor AND fname IS NOT NULL AND lname IS NOT NULL AND email IS NOT NULL AND dob IS NOT NULL AND hometown IS NOT NULL AND gender IS NOT NULL AND password IS NOT NULL)

)
```

This constraint is here to help with the ***is**\_**visitor*** column.
Our design choice of having an ***is**\_**visitor*** column is to
distinguish between a visitor and an authentic user of the Photobook
app. The value of this column (***is**\_**visitor***) is true if the
user is just a visitor, and has not registered/signed up on the system.
This helps us have a unique ***user**\_**id*** for that visitor in order
to process further operations such as adding likes and comments. In
summary, if ***is**\_**visitor*** is true, other columns can be
**NULL**, otherwise **NULL** values are not allowed (except for the
***dob*** column).

### Albums Table

The ***album**\_**id*** column serves as the primary key for the table,
ensuring each album has a unique identifier. The ***user**\_**id***
column has a foreign key constraint (***fk**\_**user**\_**id***)
referencing the ***user**\_**id*** column in the users table. This
constraint maintains referential integrity, ensuring that each album is
associated with a valid user. If a user is deleted from the users table,
all albums associated with that user will be deleted (**ON DELETE
CASCADE**).

There is a trigger (***trigger**\_**check**\_**legit**\_**user***) and a
corresponding function (***check**\_**legit**\_**user**()***) to ensure
that only non-visitor users can create albums. The trigger fires before
inserting or updating a record in the albums table, invoking the
function to check if the user creating the album is not a visitor.

### Photos Table

The ***photo**\_**id*** column serves as the primary key for the table,
ensuring each photo has a unique identifier. The ***album**\_**id***
column has a foreign key constraint (***fk**\_**album**\_**id***)
referencing the album_id column in the albums table. This constraint
ensures that each photo is associated with a valid album. If an album is
deleted, all photos associated with that album will be deleted (**ON
DELETE CASCADE**).

We are storing photos as binary strings (The **BYTEA** data type allows
storage of binary strings).

### Friends Table

The combination of ***user**\_**id*** and ***friend**\_**id*** columns
forms a composite primary key (***pk**\_**friends***), ensuring that
each friend relationship is unique. Both the ***user**\_**id*** and
***friend**\_**id*** columns have foreign key constraints
(***fk**\_**user**\_**id*** and ***fk**\_**friend**\_**id***,
respectively) referencing the ***user**\_**id*** column in the users
table. These constraints maintain referential integrity, ensuring that
both users involved in a friend relationship exist in the users table.
If a user is deleted, all friend relationships associated with that user
will be deleted (**ON DELETE CASCADE**).

We encountered an interesting edge case that we wanted to address. What
if the ***user**\_**id*** of one of the two friends is of a visitor and
not of a registered user of the system. In this case, we will need to
show an error.

To address this problem, we created a trigger
(***trigger**\_**check**\_**legit**\_**friendship***) and a
corresponding function
(***check**\_**legit**\_**friend**\_**relationship**()***) to ensure
that only non-visitor users can be friends. The trigger fires before
inserting or updating a record in the friends table, invoking the
function to check if both users involved in the friend relationship are
non-visitors.

### Tags Table

Both ***photo**\_**id*** and ***tag**\_**name*** are used as a
combination to create a composite primary key. This is because in our
design of the system we want to easily query tags based on
***photo**\_**id***s. The ***photo**\_**id*** column is a foreign key
that references the primary key of the Photos table.

### Likes Table

This table manages the likes users give to photos. We felt the need to
add this table although it wasn’t explicitly mentioned in the assignment
description.

Each like is uniquely identified by a combination of ***photo**\_**id***
and ***user**\_**id*** through a composite primary key
(***pk**\_**likes***), ensuring that a user can like a specific photo
only once. Both ***photo**\_**id*** and ***user**\_**id*** are equipped
with foreign key constraints (***fk**\_**photo**\_**id*** and
***fk**\_**user**\_**id***, respectively), which link back to the photos
and users tables to maintain referential integrity. The **ON DELETE
CASCADE** rule ensures that if a photo or user is deleted, all
associated likes are automatically removed.

### Comments Table

This table stores comments made by users on photos. Each comment is
identified by a unique ***comment**\_**id*** and includes references to
both the photo and the user through ***photo**\_**id*** and
***user**\_**id***. These columns are bound by foreign key constraints
(***fk**\_**photo**\_**id*** and ***fk**\_**user**\_**id***),
referencing the primary keys in the photos and users tables
respectively, which helps maintain data integrity. The **ON DELETE
CASCADE** option for these foreign keys ensures that any comment is
deleted if the associated photo or user is removed.
