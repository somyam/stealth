Design Documentation: 

Guild Table
-guild id (primary key)
-name
-icon_url

Channel Table
- channel id (primary key)
- guild id (foreign key)
- category
- name
- topic

User Table
- user id (primary key)
- name
- is_bot

Message Table
- message id (primary key)
- author id (foreign key)
- channel id (foreign key)
- msg_type
- content
- timestamp
- timestamp_edited 

Role Table
- role_id (primary key)
- name 
- color
- position 

User Role Table (many to many)
- user_id (foreign key)
- role_id (foreign key)
