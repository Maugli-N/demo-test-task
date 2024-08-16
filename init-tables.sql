DROP TABLE IF EXISTS message;
CREATE TABLE IF NOT EXISTS message (
  created TIMESTAMP(0) NOT NULL,
  id VARCHAR(256) NOT NULL,
  int_id VARCHAR(16) NOT NULL,
  str TEXT NOT NULL,
  status ENUM('FALSE', 'TRUE'),
  CONSTRAINT message_id_pk PRIMARY KEY(id)
) ENGINE=MyISAM DEFAULT CHARSET=cp1251;
CREATE INDEX message_created_idx ON message (created);
CREATE INDEX message_int_id_idx ON message (int_id);
DROP TABLE IF EXISTS log;
CREATE TABLE IF NOT EXISTS log (
  created TIMESTAMP(0) NOT NULL,
  int_id VARCHAR(16) NOT NULL,
  str TEXT,
  address VARCHAR(256)
) ENGINE=MyISAM DEFAULT CHARSET=cp1251;
CREATE INDEX log_address_idx USING HASH ON log (address);
