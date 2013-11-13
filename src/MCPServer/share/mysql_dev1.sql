-- Common
SET @MoveTransferToFailedLink = '61c316a6-0a50-4f65-8767-1f44b1eeb6dd';
SET @MoveSIPToFailedLink = '7d728c39-395f-4892-8193-92f086c0546f';

-- /Common

-- Issue ???
-- Add Preservation in P&A
INSERT INTO StandardTasksConfigs (pk, requiresOutputLock, execute, arguments, filterSubDir) VALUES ('7478e34b-da4b-479b-ad2e-5a3d4473364f', 0, 'normalize_v1.0', 'preservation "%fileUUID%" "%relativeLocation%" "%SIPDirectory%" "%SIPUUID%" "%taskUUID%" "original"', 'objects/');
INSERT INTO TasksConfigs (pk, taskType, taskTypePKReference, description) VALUES ('51e31d21-3e92-4c9f-8fec-740f559285f2', 'a6b1c323-7d36-428e-846a-e7e819423577', '7478e34b-da4b-479b-ad2e-5a3d4473364f', 'Normalize for preservation');
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) values ('440ef381-8fe8-4b6e-9198-270ee5653454', 'Normalize', 'Failed', '51e31d21-3e92-4c9f-8fec-740f559285f2', '39ac9205-cb08-47b1-8bc3-d3375e37d9eb');
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('b5157984-6f63-4903-a582-ff1f104e6009', '440ef381-8fe8-4b6e-9198-270ee5653454', 0, '39ac9205-cb08-47b1-8bc3-d3375e37d9eb', 'Completed successfully');
UPDATE MicroServiceChainLinksExitCodes SET nextMicroServiceChainLink='440ef381-8fe8-4b6e-9198-270ee5653454' WHERE microServiceChainLink='bcabd5e2-c93e-4aaa-af6a-9a74d54e8bf0';
-- Add Access in P&A
INSERT INTO StandardTasksConfigs (pk, requiresOutputLock, execute, arguments, filterSubDir) VALUES ('3c256437-6435-4307-9757-fbac5c07541c', 0, 'normalize_v1.0', 'access "%fileUUID%" "%relativeLocation%" "%SIPDirectory%" "%SIPUUID%" "%taskUUID%" "original"', 'objects/');
INSERT INTO TasksConfigs (pk, taskType, taskTypePKReference, description) VALUES ('2d9483ef-7dbb-4e7e-a9c6-76ed4de52da9', 'a6b1c323-7d36-428e-846a-e7e819423577', '3c256437-6435-4307-9757-fbac5c07541c', 'Normalize for access');
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) VALUES ('bcabd5e2-c93e-4aaa-af6a-9a74d54e8bf0', 'Normalize', 'Failed', '2d9483ef-7dbb-4e7e-a9c6-76ed4de52da9', '440ef381-8fe8-4b6e-9198-270ee5653454');
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('b87ee978-0f02-4852-af21-4511a43010e6', 'bcabd5e2-c93e-4aaa-af6a-9a74d54e8bf0', 0, '440ef381-8fe8-4b6e-9198-270ee5653454', 'Completed successfully');
UPDATE MicroServiceChainLinksExitCodes SET nextMicroServiceChainLink='bcabd5e2-c93e-4aaa-af6a-9a74d54e8bf0' WHERE microServiceChainLink='4103a5b0-e473-4198-8ff7-aaa6fec34749';
UPDATE MicroServiceChainLinks SET defaultNextChainLink='bcabd5e2-c93e-4aaa-af6a-9a74d54e8bf0' WHERE pk='4103a5b0-e473-4198-8ff7-aaa6fec34749';

-- Remove old normalization chains
-- This table will no longer be used
DROP TABLE TasksConfigsStartLinkForEachFile;
-- "Find access links to run"
SET @mscl1='bf11cf60-c7aa-478f-98a6-2dd9647aa35f' COLLATE utf8_unicode_ci;
SET @mscl2='eca5731c-d6a3-4e20-a83f-dde167dd7642' COLLATE utf8_unicode_ci;
-- "Find type to process as"
SET @mscl3='d02ac4b4-eb48-45ee-a1b4-ba1e9f0eff78' COLLATE utf8_unicode_ci;
-- "Find access links to run" chain that includes thumbnail/preservation
SET @mscl4='f7a8ff81-e00e-4583-857d-7d9a1fdc93f8' COLLATE utf8_unicode_ci;
SET @mscl5='760b0bcb-e001-49d1-9936-30cfe2ca0ea1' COLLATE utf8_unicode_ci;
SET @mscl6='eafd05a1-9aac-464e-83ce-a16d5429c7a1' COLLATE utf8_unicode_ci;
-- "Find thumbnail links to run"
SET @mscl7='28b9c4bc-1383-4992-9baf-c455dde1393d' COLLATE utf8_unicode_ci;
-- "Find preservation links to run"
SET @mscl8='6c4f4838-4573-4f08-8082-3aacf04f9dac' COLLATE utf8_unicode_ci;
SET @mscl9='c1fe87ad-25d4-4753-8dd5-b7b597616765' COLLATE utf8_unicode_ci;
-- "Find access links to run"
SET @mscl10='4fac5503-8fff-4c18-acf4-5b4d62654e0f' COLLATE utf8_unicode_ci;
-- "Find thumbnail links to run"
SET @mscl11='4081dc41-48df-4658-a286-0d02eca7d953' COLLATE utf8_unicode_ci;

DELETE FROM MicroServiceChainLinksExitCodes WHERE microServiceChainLink IN (@mscl1, @mscl2, @mscl3, @mscl4, @mscl5, @mscl6, @mscl7, @mscl8, @mscl9, @mscl10, @mscl11);
DELETE FROM MicroServiceChains WHERE startingLink IN (@mscl1, @mscl2, @mscl3, @mscl4, @mscl5, @mscl6, @mscl7, @mscl8, @mscl9, @mscl10, @mscl11);
DELETE FROM MicroServiceChainLinks WHERE pk IN (@mscl1, @mscl2, @mscl3, @mscl4, @mscl5, @mscl6, @mscl7, @mscl8, @mscl9, @mscl10, @mscl11);
DELETE FROM StandardTasksConfigs WHERE pk IN
(SELECT taskTypePKReference from MicroServiceChainLinks INNER JOIN TasksConfigs ON currentTask = TasksConfigs.pk
 WHERE MicroServiceChainLinks.pk IN (@mscl1, @mscl2, @mscl3, @mscl4, @mscl5, @mscl6, @mscl7, @mscl8, @mscl9, @mscl10, @mscl11));
DELETE FROM TasksConfigs WHERE pk IN
(SELECT currentTask FROM MicroServiceChainLinks WHERE MicroServiceChainLinks.pk in (@mscl1, @mscl2, @mscl3, @mscl4, @mscl5, @mscl6, @mscl7, @mscl8, @mscl9, @mscl10, @mscl11));

-- /Issue ???
