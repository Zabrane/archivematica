-- Common
SET @MoveTransferToFailedLink = '61c316a6-0a50-4f65-8767-1f44b1eeb6dd';

-- Issue 5356
CREATE TABLE TransferMetadataSets (
  pk VARCHAR(50) NOT NULL,
  createdTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  createdByUserID INT(11) NOT NULL,
  transferType VARCHAR(50) NOT NULL,
  PRIMARY KEY (pk)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE Transfers ADD COLUMN transferMetadataSetRowUUID VARCHAR(50);

CREATE TABLE TransferMetadataFields (
  pk varchar(50) NOT NULL,
  createdTime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fieldLabel VARCHAR(50) DEFAULT '',
  fieldName VARCHAR(50) NOT NULL,
  fieldType VARCHAR(50) NOT NULL,
  sortOrder INT(11) DEFAULT 0,
  PRIMARY KEY (pk)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO TransferMetadataFields (pk, createdTime, fieldLabel, fieldName, fieldType, sortOrder)
    VALUES ('fc69452c-ca57-448d-a46b-873afdd55e15', UNIX_TIMESTAMP(), 'Media number', 'media_number', 'text', 0);

INSERT INTO TransferMetadataFields (pk, createdTime, fieldLabel, fieldName, fieldType, sortOrder)
    VALUES ('a9a4efa8-d8ab-4b32-8875-b10da835621c', UNIX_TIMESTAMP(), 'Label text', 'label_text', 'textarea', 1);

INSERT INTO TransferMetadataFields (pk, createdTime, fieldLabel, fieldName, fieldType, sortOrder)
    VALUES ('367ef53b-49d6-4a4e-8b2f-10267d6a7db1', UNIX_TIMESTAMP(), 'Media manufacture', 'media_manufacture', 'text', 2);

INSERT INTO TransferMetadataFields (pk, createdTime, fieldLabel, fieldName, fieldType, sortOrder)
    VALUES ('277727e4-b621-4f68-acb4-5689f81f31cd', UNIX_TIMESTAMP(), 'Serial number', 'serial_number', 'text', 3);

CREATE TABLE TransferMetadataFieldValues (
  pk varchar(50) NOT NULL,
  createdTime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  setUUID VARCHAR(50) NOT NULL,
  filePath longtext NOT NULL,
  fieldUUID VARCHAR(50) NOT NULL,
  fieldValue LONGTEXT DEFAULT '',
  PRIMARY KEY (pk)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
-- /Issue 5356
