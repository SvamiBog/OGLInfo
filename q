                                           Table "public.autoad"
     Column      |            Type             | Collation | Nullable |              Default               
-----------------+-----------------------------+-----------+----------+------------------------------------
 id              | integer                     |           | not null | nextval('autoad_id_seq'::regclass)
 title           | character varying           |           | not null | 
 price           | double precision            |           |          | 
 currency        | character varying           |           |          | 
 location        | character varying           |           |          | 
 country         | character varying           |           |          | 
 url             | character varying           |           | not null | 
 created_at      | timestamp without time zone |           | not null | 
 brand           | character varying           |           |          | 
 model           | character varying           |           |          | 
 year            | integer                     |           |          | 
 mileage         | integer                     |           |          | 
 mileage_unit    | character varying           |           |          | 
 fuel            | character varying           |           |          | 
 transmission    | character varying           |           |          | 
 drive           | character varying           |           |          | 
 engine_capacity | double precision            |           |          | 
 power           | integer                     |           |          | 
 body_type       | character varying           |           |          | 
 doors           | integer                     |           |          | 
 color           | character varying           |           |          | 
 description     | character varying           |           |          | 
 dealer          | character varying           |           |          | 
 condition       | character varying           |           |          | 
 platform        | character varying           |           |          | 
 sold_at         | timestamp without time zone |           |          | 
Indexes:
    "autoad_pkey" PRIMARY KEY, btree (id)
    "ix_autoad_url" UNIQUE, btree (url)

