A few constraints:

For the albums table, if a user is deleted, all their albums will also be deleted (ON DELETE CASCADE).
For the photos table, if an album is deleted, all its photos will also be deleted (ON DELETE CASCADE).
For the friends table, if a user is deleted, all their friend relationships will also be deleted (ON DELETE CASCADE).
For the tags table, if a photo is deleted, all its tags will also be deleted (ON DELETE CASCADE).
For the comments table, if a photo or a user is deleted, all related comments will also be deleted (ON DELETE CASCADE).
For the likes table, if a photo or a user is deleted, all related likes will also be deleted (ON DELETE CASCADE).



- environment ( use global)
- install -r requirements 
- run flask (python3 -m flask run)