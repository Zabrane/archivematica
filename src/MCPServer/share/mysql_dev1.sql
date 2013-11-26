-- Common
SET @MoveTransferToFailedLink = '61c316a6-0a50-4f65-8767-1f44b1eeb6dd';
SET @MoveSIPToFailedLink = '7d728c39-395f-4892-8193-92f086c0546f';
-- /Common

-- Issue 5216

-- Add Chain Choice for 'Add manual normalization metadata'
-- MSCL move to watched dir - terminate
INSERT INTO StandardTasksConfigs (pk, requiresOutputLock, execute, arguments) VALUES ('38920eaa-09a2-470c-bb3d-791d66ec359c', 0, 'moveSIP_v0.0', '"%SIPDirectory%" "%sharedPath%watchedDirectories/manualNormalizationMetadata/." "%SIPUUID%" "%sharedPath%" "%SIPUUID%" "%sharedPath%"');
INSERT INTO TasksConfigs (pk, taskType, taskTypePKReference, description) VALUES ('fa8b1f81-0d79-4f9a-a888-fc3292f2d992', '36b2e239-4a57-4aa5-8ebc-7a29139baca6', '38920eaa-09a2-470c-bb3d-791d66ec359c', 'Move to manual normalization metadata directory');
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) VALUES ('b366e9c5-95f6-49f1-957c-a8f7bb601120', 'Normalize', 'Failed', 'fa8b1f81-0d79-4f9a-a888-fc3292f2d992', @MoveSIPToFailedLink);
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('5ce2e89a-ea14-4445-bc92-d287bf02afb3', 'b366e9c5-95f6-49f1-957c-a8f7bb601120', 0, NULL, 'Completed successfully');
UPDATE MicroServiceChainLinksExitCodes SET nextMicroServiceChainLink='b366e9c5-95f6-49f1-957c-a8f7bb601120' WHERE microServiceChainLink='91ca6f1f-feb5-485d-99d2-25eed195e330';
-- MSCL move currently processing
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) VALUES ('50ddfe31-de9d-4a25-b0aa-fd802520607b', 'Normalize', 'Failed', '74146fe4-365d-4f14-9aae-21eafa7d8393', @MoveSIPToFailedLink);
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('8008c4a7-bea2-43b0-83ff-b6df0ceb3937', '50ddfe31-de9d-4a25-b0aa-fd802520607b', 0, 'ab0d3815-a9a3-43e1-9203-23a40c00c551', 'Completed successfully');
-- MSCL done MN metadata - Use replacement dict since only one path
INSERT INTO TasksConfigs (pk, taskType, taskTypePKReference, description) VALUES ('71d0caff-1257-4843-8df7-82615724d5a5', '9c84b047-9a6d-463f-9836-eafa49743b84', 'a9d91e76-8639-4cfa-9189-54c139cbac60', 'Add manual normalization metadata?');
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) VALUES ('a50570ee-2acf-4205-81fd-ddf11c1a6582', 'Normalize', 'Failed', '71d0caff-1257-4843-8df7-82615724d5a5', @MoveSIPToFailedLink);
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('8b65763d-de29-4ce8-b42f-9e244d6d701f', 'a50570ee-2acf-4205-81fd-ddf11c1a6582', 0, '50ddfe31-de9d-4a25-b0aa-fd802520607b', 'Completed successfully');
INSERT INTO MicroServiceChoiceReplacementDic (pk, choiceAvailableAtLink, description, replacementDic) VALUES ('a9d91e76-8639-4cfa-9189-54c139cbac60', 'a50570ee-2acf-4205-81fd-ddf11c1a6582', 'Metadata entered', '{"%Unused%":"%Unused%"}');
-- MSC manual normalization event detail chain
INSERT INTO MicroServiceChains (pk, startingLink, description) VALUES ('e2382ce4-6ee0-4445-aca3-0764ebae94ac', 'a50570ee-2acf-4205-81fd-ddf11c1a6582', 'Manual normalization metadata entry wait');
-- WatchedDir to start up Add manual normalization metadata chain
INSERT INTO WatchedDirectories (pk, watchedDirectoryPath, chain, expectedType) VALUES ('0a621b7d-6cbd-4193-b1d4-b4b90fbc2461', '%watchDirectoryPath%manualNormalizationMetadata/', 'e2382ce4-6ee0-4445-aca3-0764ebae94ac', '76e66677-40e6-41da-be15-709afb334936');

-- /Issue 5216
