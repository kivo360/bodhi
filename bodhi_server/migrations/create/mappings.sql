
CREATE TABLE mappings (
	id UUID NOT NULL, 
	key_name VARCHAR NOT NULL, 
	key_id VARCHAR NOT NULL, 
	value_name VARCHAR NOT NULL, 
	value_type VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (id)
)

