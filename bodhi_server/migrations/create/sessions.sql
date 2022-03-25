
CREATE TABLE sessions (
	id UUID NOT NULL, 
	num_episodes INTEGER NOT NULL, 
	is_finished BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (id)
)

