-- Common
SET @MoveTransferToFailedLink = '61c316a6-0a50-4f65-8767-1f44b1eeb6dd';
SET @MoveSIPToFailedLink = '7d728c39-395f-4892-8193-92f086c0546f';
-- /Common

-- Issue 5955
-- Fix group on METS gen
UPDATE MicroServiceChainLinks SET microserviceGroup = "Prepare AIP" WHERE pk IN ('ccf8ec5c-3a9a-404a-a7e7-8f567d3b36a0', '65240550-d745-4afe-848f-2bf5910457c9');
-- /Issue 5955

-- Issue 5803 AIC

-- Create METS.xml file
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) VALUES ('53e14112-21bb-46f0-aed3-4e8c2de6678f', 'Prepare AIC', 'Failed', '23650e92-092d-4ace-adcc-c627c41b127e', @MoveSIPToFailedLink);
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('27e94795-ae8e-4e7d-942f-346024167c76', '53e14112-21bb-46f0-aed3-4e8c2de6678f', 0, '3ba518ab-fc47-4cba-9b5c-79629adac10b', 'Completed successfully');
-- Create thumbnail dir
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) VALUES ('9e810686-d747-4da1-9908-876fb89ac78e', 'Prepare AIC', 'Failed', 'ea463bfd-5fa2-4936-b8c3-1ce3b74303cf', @MoveSIPToFailedLink);
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('0b689082-e35b-4bc5-b2da-6773398ea6a7', '9e810686-d747-4da1-9908-876fb89ac78e', 0, '53e14112-21bb-46f0-aed3-4e8c2de6678f', 'Completed successfully');
-- Insert create AIC METS MSCL
INSERT INTO StandardTasksConfigs (pk, requiresOutputLock, execute, arguments) VALUES ('77e6b5ec-acf7-44d0-b250-32cbe014499d', 0, 'createAIC_METS_v1.0', '"%SIPUUID%" "%SIPDirectory%"');
INSERT INTO TasksConfigs (pk, taskType, taskTypePKReference, description) VALUES ('741a09ee-8143-4216-8919-1046571af3e9', '36b2e239-4a57-4aa5-8ebc-7a29139baca6', '77e6b5ec-acf7-44d0-b250-32cbe014499d', 'Create AIC METS file');
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) VALUES ('142d0a36-2b88-4b98-8a33-d809f667ecef', 'Prepare AIC', 'Failed', '741a09ee-8143-4216-8919-1046571af3e9', @MoveSIPToFailedLink);
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('bff46a44-5493-4217-b858-81e840f1ca8b', '142d0a36-2b88-4b98-8a33-d809f667ecef', 0, '9e810686-d747-4da1-9908-876fb89ac78e', 'Completed successfully');
-- Include default SIP processingMCP
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) VALUES ('d29105f0-161d-449d-9c34-5a5ea3263f8e', 'Prepare AIC', 'Failed', 'f89b9e0f-8789-4292-b5d0-4a330c0205e1', '142d0a36-2b88-4b98-8a33-d809f667ecef');
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('1977601d-0a2d-4ccc-9aa6-571d4b6b0804', 'd29105f0-161d-449d-9c34-5a5ea3263f8e', 0, '142d0a36-2b88-4b98-8a33-d809f667ecef', 'Completed successfully');
-- Restructure for compliance
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) VALUES ('0c2c9c9a-25b2-4a2d-a790-103da79f9604', 'Prepare AIC', 'Failed', '3ae4931e-886e-4e0a-9a85-9b047c9983ac', @MoveSIPToFailedLink);
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('b981edfd-d9d8-498f-a7f2-1765d6833923', '0c2c9c9a-25b2-4a2d-a790-103da79f9604', 0, 'd29105f0-161d-449d-9c34-5a5ea3263f8e', 'Completed successfully');
-- Move to processing dir
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) VALUES ('efd15406-fd6c-425b-8772-d460e1e79009', 'Prepare AIC', 'Failed', '74146fe4-365d-4f14-9aae-21eafa7d8393', @MoveSIPToFailedLink);
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('7941ee5a-f093-4cfb-bacc-03dfb7d51e15', 'efd15406-fd6c-425b-8772-d460e1e79009', 0, '0c2c9c9a-25b2-4a2d-a790-103da79f9604', 'Completed successfully');
-- Set permissions
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) VALUES ('f8cb20e6-27aa-44f6-b5a1-dd53b5fc71f6', 'Prepare AIC', 'Failed', 'ad38cdea-d1da-4d06-a7e5-6f75da85a718', @MoveSIPToFailedLink);
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, nextMicroServiceChainLink, exitMessage) VALUES ('4aa64bfe-3574-4bd4-8f6f-7c4cb0575f85', 'f8cb20e6-27aa-44f6-b5a1-dd53b5fc71f6', 0, 'efd15406-fd6c-425b-8772-d460e1e79009', 'Completed successfully');
-- Approve/reject AIC
INSERT INTO TasksConfigs (pk, taskType, taskTypePKReference, description) VALUES ('81f2a21b-a7a0-44e4-a2f6-9a6cf742b052', '61fb3874-8ef6-49d3-8a2d-3cb66e86a30c', NULL, 'Approve AIC');
INSERT INTO MicroServiceChainLinks(pk, microserviceGroup, defaultExitMessage, currentTask, defaultNextChainLink) VALUES ('6404ce13-8619-48ba-b12f-aa7a034153ac', 'Approve AIC', 'Failed', '81f2a21b-a7a0-44e4-a2f6-9a6cf742b052', @MoveSIPToFailedLink);
-- Reject AIC choice
INSERT INTO MicroServiceChainChoice(pk, choiceAvailableAtLink, chainAvailable) VALUES ('e981fb29-7f93-4719-99ba-f2d22455f3ed', '6404ce13-8619-48ba-b12f-aa7a034153ac', '169a5448-c756-4705-a920-737de6b8d595');
-- Approve AIC choice
INSERT INTO MicroServiceChains(pk, startingLink, description) VALUES ('5f34245e-5864-4199-aafc-bc0ada01d4cd', 'f8cb20e6-27aa-44f6-b5a1-dd53b5fc71f6', 'Approve AIC');
INSERT INTO MicroServiceChainChoice(pk, choiceAvailableAtLink, chainAvailable) VALUES ('bebc5174-09b8-49e6-8dd6-4896e49fdc5e', '6404ce13-8619-48ba-b12f-aa7a034153ac', '5f34245e-5864-4199-aafc-bc0ada01d4cd');

-- Add WatchedDir MSC
INSERT INTO MicroServiceChains(pk, startingLink, description) VALUES ('0766af55-a950-44d0-a79b-9f2bb65f92c8', '6404ce13-8619-48ba-b12f-aa7a034153ac', 'Create AIC');
-- WatchedDirectory
INSERT INTO WatchedDirectories(pk, watchedDirectoryPath, chain, expectedType) VALUES ('aae2a1df-b012-492d-8d84-4fd9bcc25b71', '%watchDirectoryPath%system/createAIC/', '0766af55-a950-44d0-a79b-9f2bb65f92c8', '76e66677-40e6-41da-be15-709afb334936');

-- Add Part of AIC to Dublin Core
ALTER TABLE Dublincore ADD isPartOf longtext;

-- Updated bagit command to put metadata/ in the payload too
UPDATE StandardTasksConfigs SET arguments='create "%SIPDirectory%%SIPName%-%SIPUUID%" "%SIPLogsDirectory%" "%SIPObjectsDirectory%" "%SIPDirectory%METS.%SIPUUID%.xml" "%SIPDirectory%thumbnails/" "%SIPDirectory%metadata/" --writer filesystem --payloadmanifestalgorithm "sha512"' WHERE pk='045f84de-2669-4dbc-a31b-43a4954d0481';

-- Add sipType to SIPs table
ALTER TABLE SIPs ADD sipType varchar(8);

-- /Issue 5803 AIC
