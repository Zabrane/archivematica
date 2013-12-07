-- Common
SET @MoveTransferToFailedLink = '61c316a6-0a50-4f65-8767-1f44b1eeb6dd';
SET @MoveSIPToFailedLink = '7d728c39-395f-4892-8193-92f086c0546f';
-- /Common

-- Issue 6020

-- Updated remove unneeded files to remove excess args
UPDATE StandardTasksConfigs SET arguments='"%relativeLocation%" "%fileUUID%"' WHERE pk='49b803e3-8342-4098-bb3f-434e1eb5cfa8';

-- Add remove unneeded files to Transfer, before file ID
INSERT INTO StandardTasksConfigs (pk, requiresOutputLock, execute, arguments) VALUES ('66aa823d-3b72-4d13-9ad6-c5e6580857b8', 1, 'removeUnneededFiles_v0.0', '"%relativeLocation%" "%fileUUID%"'); -- not in objects/
INSERT INTO TasksConfigs (pk, taskType, taskTypePKReference, description) VALUES ('85308c8b-b299-4453-bf40-9ac61d134015', 'a6b1c323-7d36-428e-846a-e7e819423577', '66aa823d-3b72-4d13-9ad6-c5e6580857b8', 'Remove unneeded files');
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) VALUES ('5d780c7d-39d0-4f4a-922b-9d1b0d217bca', 'Verify transfer compliance', 'Failed', '85308c8b-b299-4453-bf40-9ac61d134015', 'ea0e8838-ad3a-4bdd-be14-e5dba5a4ae0c');
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('9cb81a5c-a7a1-43a8-8eb6-3e999923e03c', '5d780c7d-39d0-4f4a-922b-9d1b0d217bca', 0, 'ea0e8838-ad3a-4bdd-be14-e5dba5a4ae0c', 'Completed successfully');
UPDATE MicroServiceChainLinksExitCodes SET nextMicroServiceChainLink='5d780c7d-39d0-4f4a-922b-9d1b0d217bca' WHERE microServiceChainLink='50b67418-cb8d-434d-acc9-4a8324e7fdd2';
UPDATE MicroServiceChainLinks SET defaultNextChainLink='5d780c7d-39d0-4f4a-922b-9d1b0d217bca' WHERE pk='50b67418-cb8d-434d-acc9-4a8324e7fdd2';

-- Add remove unneeded and hidden files to Transfer after extract
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) VALUES ('bdce640d-6e94-49fe-9300-3192a7e5edac', 'Extract packages', 'Failed', 'ef0bb0cf-28d5-4687-a13d-2377341371b5', 'aaa929e4-5c35-447e-816a-033a66b9b90b');
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('9a07d5a1-1418-4007-9c7e-55462ca63751', 'bdce640d-6e94-49fe-9300-3192a7e5edac', 0, 'aaa929e4-5c35-447e-816a-033a66b9b90b', 'Completed successfully');
UPDATE MicroServiceChainLinksExitCodes SET nextMicroServiceChainLink='bdce640d-6e94-49fe-9300-3192a7e5edac' WHERE microServiceChainLink='c5ecb5a9-d697-4188-844f-9a756d8734fa';
UPDATE MicroServiceChainLinks SET defaultNextChainLink='bdce640d-6e94-49fe-9300-3192a7e5edac' WHERE pk='c5ecb5a9-d697-4188-844f-9a756d8734fa';
-- Update for maildir
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) VALUES ('e19f8eed-faf9-4e04-bf1f-e9418f2b2b11', 'Extract packages', 'Failed', 'ef0bb0cf-28d5-4687-a13d-2377341371b5', '22ded604-6cc0-444b-b320-f96afb15d581');
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('0ef15153-0d41-4b93-bdb3-4158cec405a3', 'e19f8eed-faf9-4e04-bf1f-e9418f2b2b11', 0, '22ded604-6cc0-444b-b320-f96afb15d581', 'Completed successfully');
UPDATE MicroServiceChainLinksExitCodes SET nextMicroServiceChainLink='e19f8eed-faf9-4e04-bf1f-e9418f2b2b11' WHERE microServiceChainLink='01b30826-bfc4-4e07-8ca2-4263debad642';
UPDATE MicroServiceChainLinks SET defaultNextChainLink='e19f8eed-faf9-4e04-bf1f-e9418f2b2b11' WHERE pk='01b30826-bfc4-4e07-8ca2-4263debad642';

-- /Issue 6020

-- Issue 5866 - Customizeable FPR characterization
-- Inserts a new TasksConfigs entry for the new "Characterize and extract metadata", replacing archivematicaFITS
SET @characterizeSTC = 'd6307888-f5ef-4828-80d6-fb6f707ae023' COLLATE utf8_unicode_ci;
SET @characterizeTC = '00041f5a-42cd-4b77-a6d4-6ef0f376a817' COLLATE utf8_unicode_ci;
SET @characterizeExtractMetadata='303a65f6-a16f-4a06-807b-cb3425a30201' COLLATE utf8_unicode_ci;
INSERT INTO StandardTasksConfigs (pk, requiresOutputLock, execute, arguments, filterSubDir) VALUES (@characterizeSTC, 0, 'characterizeFile_v0.0', '"%relativeLocation%" "%fileUUID%"', 'objects');
INSERT INTO TasksConfigs (pk, taskType, taskTypePKReference, description) VALUES (@characterizeTC, 'a6b1c323-7d36-428e-846a-e7e819423577', @characterizeSTC, "Characterize and extract metadata");
UPDATE MicroServiceChainLinks SET currentTask=@characterizeTC WHERE pk=@characterizeExtractMetadata;

-- Issue 5880
-- Insert the new "Examine contents" step immediately following characterization.
-- This runs bulk_extractor currently, but may be expanded into running other tools in the future.
SET @examineContentsMSCL = '100a75f4-9d2a-41bf-8dd0-aec811ae1077' COLLATE utf8_unicode_ci;
INSERT INTO StandardTasksConfigs (pk, requiresOutputLock, execute, arguments, filterSubDir) VALUES ('3a17cc3f-eabc-4b58-90e8-1df2a96cf182', 0, 'examineContents_v0.0', '"%relativeLocation%" "%SIPDirectory%" "%fileUUID%"', 'objects');
INSERT INTO TasksConfigs (pk, taskType, taskTypePKReference, description) VALUES ('869c4c44-6e7d-4473-934d-80c7b95a8310', 'a6b1c323-7d36-428e-846a-e7e819423577', '3a17cc3f-eabc-4b58-90e8-1df2a96cf182', 'Examine contents');
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) values (@examineContentsMSCL, 'Characterize and extract metadata', 'Failed', '869c4c44-6e7d-4473-934d-80c7b95a8310', '1b1a4565-b501-407b-b40f-2f20889423f1');
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('87dcd08a-7688-425a-ae5f-2f623feb078a', @examineContentsMSCL, 0, '1b1a4565-b501-407b-b40f-2f20889423f1', 'Completed successfully');
-- Characterize and extract (normal)
UPDATE MicroServiceChainLinksExitCodes SET nextMicroServiceChainLink=@examineContentsMSCL WHERE microServiceChainLink='303a65f6-a16f-4a06-807b-cb3425a30201';
-- Characterize and extract (maildir)
UPDATE MicroServiceChainLinksExitCodes SET nextMicroServiceChainLink=@examineContentsMSCL WHERE microServiceChainLink='bd382151-afd0-41bf-bb7a-b39aef728a32';

-- Insert a "Examine contents?" choice
SET @examineContentsChoice = 'accea2bf-ba74-4a3a-bb97-614775c74459' COLLATE utf8_unicode_ci;
SET @examineContentsType = '7569eff6-401f-11e3-ae52-1c6f65d9668b' COLLATE utf8_unicode_ci;
-- First we create new chains - one for examination, one that picks back up immediately following examination
SET @examineChoiceChain = '96b49116-b114-47e8-95d0-b3c6ae4e80f5' COLLATE utf8_unicode_ci;
SET @examineChain = '06f03bb3-121d-4c85-bec7-abbc5320a409' COLLATE utf8_unicode_ci;
SET @postExamineChain = 'e0a39199-c62a-4a2f-98de-e9d1116460a8' COLLATE utf8_unicode_ci;
INSERT INTO MicroServiceChains (pk, startingLink, description) VALUES (@examineChain, @examineContentsMSCL, 'Examine contents');
INSERT INTO MicroServiceChains (pk, startingLink, description) VALUES (@postExamineChain, '1b1a4565-b501-407b-b40f-2f20889423f1', 'Skip examine contents');

-- Next we make sure we move it into a new watched directory before executing the choice
SET @examineContentsWatchDirectorySTC = 'f62e7309-61b3-4318-a770-ab40595bc7b8' COLLATE utf8_unicode_ci;
SET @examineContentsWatchDirectoryTC = '08fc82e7-bc15-4608-8171-50475e8071e2' COLLATE utf8_unicode_ci;
SET @examineContentsWatchDirectoryMSCL = 'dae3c416-a8c2-4515-9081-6dbd7b265388' COLLATE utf8_unicode_ci;
INSERT INTO StandardTasksConfigs (pk, requiresOutputLock, execute, arguments) VALUES (@examineContentsWatchDirectorySTC, 0, 'moveTransfer_v0.0', '"%SIPDirectory%" "%sharedPath%watchedDirectories/workFlowDecisions/examineContentsChoice/."  "%SIPUUID%" "%sharedPath%"');
INSERT INTO TasksConfigs (pk, taskType, taskTypePKReference, description) VALUES (@examineContentsWatchDirectoryTC, '36b2e239-4a57-4aa5-8ebc-7a29139baca6', @examineContentsWatchDirectorySTC, 'Move to examine contents');
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) VALUES (@examineContentsWatchDirectoryMSCL, 'Examine contents', 'Failed', @examineContentsWatchDirectoryTC, @MoveTransferToFailedLink);
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('72559113-a0a6-4ba8-8b17-c855389e5f16', @examineContentsWatchDirectoryMSCL, 0, NULL, 'Completed successfully');

-- Next create the choice itself and point the chains there
INSERT INTO TasksConfigs (pk, taskType, description) VALUES (@examineContentsType, '61fb3874-8ef6-49d3-8a2d-3cb66e86a30c', 'Examine contents?');
INSERT INTO MicroServiceChainLinks (pk, microserviceGroup, defaultExitMessage, currentTask) VALUES (@examineContentsChoice, 'Examine contents', 'Failed', @examineContentsType);

-- New watched directory entry, pointing at this chainlink
INSERT INTO MicroServiceChains (pk, startingLink, description) VALUES (@examineChoiceChain, @examineContentsChoice, 'Examine contents?');
INSERT INTO WatchedDirectories(pk, watchedDirectoryPath, chain, expectedType) VALUES ('da0ce3b8-07c4-4a89-8313-15df5884ac48', "%watchDirectoryPath%workFlowDecisions/examineContentsChoice/", @examineChoiceChain, 'f9a3a93b-f184-4048-8072-115ffac06b5d');

-- Insert the two choices - examine, or don't examine
INSERT INTO MicroServiceChainChoice (pk, choiceAvailableAtLink, chainAvailable) VALUES ('913ee4f7-35f4-44a0-9249-eb1cfc270d4e', @examineContentsChoice, @examineChain);
INSERT INTO MicroServiceChainChoice (pk, choiceAvailableAtLink, chainAvailable) VALUES ('64e33508-c51d-4d96-9523-1a0c3b0809b1', @examineContentsChoice, @postExamineChain);
UPDATE MicroServiceChainLinksExitCodes SET nextMicroServiceChainLink=@examineContentsWatchDirectoryMSCL WHERE nextMicroServiceChainLink=@examineContentsMSCL;

-- Ensure the default link for "Characterize and extract metadata" goes to a sensible place
UPDATE MicroServiceChainLinks SET defaultNextChainLink=@examineContentsWatchDirectoryMSCL WHERE pk=@characterizeExtractMetadata;

-- /Issue 5880
