
CREATE TABLE unstructured (
	id UUID NOT NULL, 
	data JSONB, 
	tags JSONB, 
	bucket TEXT NOT NULL, 
	reference_time TIMESTAMP WITH TIME ZONE NOT NULL, 
	insert_time TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (id)
)