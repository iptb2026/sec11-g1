-- MariaDB dump 10.19  Distrib 10.4.27-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: toyongan
-- ------------------------------------------------------
-- Server version	10.4.27-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `toyongan`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `toyongan` /*!40100 DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci */;

USE `toyongan`;

--
-- Table structure for table `account_types`
--

DROP TABLE IF EXISTS `account_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account_types` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `type_code` varchar(50) NOT NULL,
  `type_name` varchar(100) NOT NULL,
  `minimum_balance` decimal(18,2) DEFAULT NULL,
  `opening_deposit` decimal(18,2) DEFAULT NULL,
  `annual_interest_rate` decimal(5,2) DEFAULT NULL,
  `daily_withdrawal_limit` decimal(18,2) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `type_code` (`type_code`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_types`
--

LOCK TABLES `account_types` WRITE;
/*!40000 ALTER TABLE `account_types` DISABLE KEYS */;
INSERT INTO `account_types` VALUES (1,'SAVINGS','Regular Savings Account',500.00,1000.00,1.50,50000.00,'2026-08-27 07:45:52');
/*!40000 ALTER TABLE `account_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `account_number` varchar(30) NOT NULL,
  `customer_id` bigint(20) NOT NULL,
  `account_type_id` bigint(20) NOT NULL,
  `available_balance` decimal(18,2) DEFAULT NULL,
  `ledger_balance` decimal(18,2) DEFAULT NULL,
  `currency_code` varchar(10) DEFAULT NULL,
  `status` enum('ACTIVE','FROZEN','CLOSED') DEFAULT NULL,
  `opened_at` timestamp NULL DEFAULT current_timestamp(),
  `closed_at` datetime DEFAULT NULL,
  `branch_code` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `account_number` (`account_number`),
  KEY `customer_id` (`customer_id`),
  KEY `account_type_id` (`account_type_id`),
  CONSTRAINT `accounts_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `users` (`id`),
  CONSTRAINT `accounts_ibfk_2` FOREIGN KEY (`account_type_id`) REFERENCES `account_types` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts`
--

LOCK TABLES `accounts` WRITE;
/*!40000 ALTER TABLE `accounts` DISABLE KEYS */;
INSERT INTO `accounts` VALUES (1,'1000-2026-0001',3,1,26498.25,26498.25,'PHP','ACTIVE','2026-08-27 07:45:52',NULL,'MAIN-01'),(2,'1000-2026-0002',3,1,3000.00,3000.00,'PHP','ACTIVE','2026-08-27 07:47:37',NULL,'MAIN-01');
/*!40000 ALTER TABLE `accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `audit_logs` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `action_type` varchar(100) NOT NULL,
  `entity_name` varchar(100) NOT NULL,
  `entity_id` bigint(20) DEFAULT NULL,
  `old_value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`old_value`)),
  `new_value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`new_value`)),
  `ip_address` varchar(50) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `action_timestamp` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `audit_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_logs`
--

LOCK TABLES `audit_logs` WRITE;
/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
INSERT INTO `audit_logs` VALUES (1,1,'TEST_ACTION','SYSTEM',1,'null','{\"msg\": \"Initialized Dry Run Test\"}',NULL,NULL,'2026-08-27 07:47:37'),(2,1,'TEST_ACTION','SYSTEM',1,'null','{\"msg\": \"Initialized Dry Run Test\"}',NULL,NULL,'2026-08-27 07:48:10');
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `banks`
--

DROP TABLE IF EXISTS `banks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `banks` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `bank_code` varchar(50) NOT NULL,
  `swift_code` varchar(50) DEFAULT NULL,
  `bank_name` varchar(150) NOT NULL,
  `short_name` varchar(100) DEFAULT NULL,
  `api_endpoint` varchar(255) DEFAULT NULL,
  `contact_email` varchar(150) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `bank_code` (`bank_code`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `banks`
--

LOCK TABLES `banks` WRITE;
/*!40000 ALTER TABLE `banks` DISABLE KEYS */;
INSERT INTO `banks` VALUES (1,'BDO',NULL,'Banco de Oro Universal Bank','BDO',NULL,NULL,'ACTIVE','2026-08-27 07:45:52');
/*!40000 ALTER TABLE `banks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deposits`
--

DROP TABLE IF EXISTS `deposits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `deposits` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `account_id` bigint(20) NOT NULL,
  `reference_number` varchar(100) NOT NULL,
  `amount` decimal(18,2) NOT NULL,
  `deposit_channel` enum('CASH','ATM','ONLINE','INTERBANK') NOT NULL,
  `deposited_by_user_id` bigint(20) DEFAULT NULL,
  `remarks` text DEFAULT NULL,
  `transaction_date` datetime NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `reference_number` (`reference_number`),
  KEY `account_id` (`account_id`),
  KEY `deposited_by_user_id` (`deposited_by_user_id`),
  CONSTRAINT `deposits_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  CONSTRAINT `deposits_ibfk_2` FOREIGN KEY (`deposited_by_user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deposits`
--

LOCK TABLES `deposits` WRITE;
/*!40000 ALTER TABLE `deposits` DISABLE KEYS */;
INSERT INTO `deposits` VALUES (1,1,'DEP-TEST-1',5000.00,'CASH',NULL,'Dry-run test deposit','2026-08-27 07:48:11','2026-08-27 07:48:11');
/*!40000 ALTER TABLE `deposits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fee_records`
--

DROP TABLE IF EXISTS `fee_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fee_records` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `account_id` bigint(20) NOT NULL,
  `fee_type_id` bigint(20) NOT NULL,
  `transaction_reference` varchar(100) DEFAULT NULL,
  `amount_charged` decimal(18,2) NOT NULL,
  `charged_at` timestamp NULL DEFAULT current_timestamp(),
  `remarks` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  KEY `fee_type_id` (`fee_type_id`),
  CONSTRAINT `fee_records_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  CONSTRAINT `fee_records_ibfk_2` FOREIGN KEY (`fee_type_id`) REFERENCES `fee_types` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fee_records`
--

LOCK TABLES `fee_records` WRITE;
/*!40000 ALTER TABLE `fee_records` DISABLE KEYS */;
INSERT INTO `fee_records` VALUES (1,1,1,NULL,18.00,'2026-08-27 07:48:11','Monthly maintenance / ATM fee');
/*!40000 ALTER TABLE `fee_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fee_types`
--

DROP TABLE IF EXISTS `fee_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fee_types` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fee_code` varchar(50) NOT NULL,
  `fee_name` varchar(100) NOT NULL,
  `fee_description` text DEFAULT NULL,
  `fixed_amount` decimal(18,2) DEFAULT NULL,
  `percentage_rate` decimal(5,2) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `fee_code` (`fee_code`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fee_types`
--

LOCK TABLES `fee_types` WRITE;
/*!40000 ALTER TABLE `fee_types` DISABLE KEYS */;
INSERT INTO `fee_types` VALUES (1,'ATM_FEE','ATM Withdrawal Fee','Fee for interbank ATM withdrawal',18.00,0.00,'2026-08-27 07:47:28');
/*!40000 ALTER TABLE `fee_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interbank_transfers`
--

DROP TABLE IF EXISTS `interbank_transfers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `interbank_transfers` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `source_account_id` bigint(20) NOT NULL,
  `target_bank_id` bigint(20) NOT NULL,
  `target_account_number` varchar(50) NOT NULL,
  `beneficiary_name` varchar(150) DEFAULT NULL,
  `reference_number` varchar(100) NOT NULL,
  `amount` decimal(18,2) NOT NULL,
  `transfer_fee` decimal(18,2) DEFAULT NULL,
  `status` enum('PENDING','VERIFIED','PROCESSING','SUCCESS','FAILED','REVERSED') DEFAULT NULL,
  `initiated_at` timestamp NULL DEFAULT current_timestamp(),
  `completed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reference_number` (`reference_number`),
  KEY `source_account_id` (`source_account_id`),
  KEY `target_bank_id` (`target_bank_id`),
  CONSTRAINT `interbank_transfers_ibfk_1` FOREIGN KEY (`source_account_id`) REFERENCES `accounts` (`id`),
  CONSTRAINT `interbank_transfers_ibfk_2` FOREIGN KEY (`target_bank_id`) REFERENCES `banks` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interbank_transfers`
--

LOCK TABLES `interbank_transfers` WRITE;
/*!40000 ALTER TABLE `interbank_transfers` DISABLE KEYS */;
INSERT INTO `interbank_transfers` VALUES (1,1,1,'9999-8888-7777','Maria Santos','IB-TEST-1',500.00,15.00,'SUCCESS','2026-08-27 07:48:11','2026-08-27 07:48:11');
/*!40000 ALTER TABLE `interbank_transfers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interest_policies`
--

DROP TABLE IF EXISTS `interest_policies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `interest_policies` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `account_type_id` bigint(20) NOT NULL,
  `policy_name` varchar(100) NOT NULL,
  `annual_rate` decimal(5,2) NOT NULL,
  `compounding_frequency` enum('DAILY','MONTHLY','QUARTERLY','YEARLY') DEFAULT NULL,
  `effective_date` date NOT NULL,
  `expiration_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `account_type_id` (`account_type_id`),
  CONSTRAINT `interest_policies_ibfk_1` FOREIGN KEY (`account_type_id`) REFERENCES `account_types` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interest_policies`
--

LOCK TABLES `interest_policies` WRITE;
/*!40000 ALTER TABLE `interest_policies` DISABLE KEYS */;
INSERT INTO `interest_policies` VALUES (1,1,'Standard Savings Interest 1.5%',1.50,'MONTHLY','2026-08-01',NULL);
/*!40000 ALTER TABLE `interest_policies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interest_records`
--

DROP TABLE IF EXISTS `interest_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `interest_records` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `account_id` bigint(20) NOT NULL,
  `policy_id` bigint(20) NOT NULL,
  `amount_credited` decimal(18,2) NOT NULL,
  `balance_before` decimal(18,2) NOT NULL,
  `balance_after` decimal(18,2) NOT NULL,
  `credited_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  KEY `policy_id` (`policy_id`),
  CONSTRAINT `interest_records_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  CONSTRAINT `interest_records_ibfk_2` FOREIGN KEY (`policy_id`) REFERENCES `interest_policies` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interest_records`
--

LOCK TABLES `interest_records` WRITE;
/*!40000 ALTER TABLE `interest_records` DISABLE KEYS */;
INSERT INTO `interest_records` VALUES (1,1,1,31.25,26467.00,26498.25,'2026-08-27 07:48:11');
/*!40000 ALTER TABLE `interest_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ledger_entries`
--

DROP TABLE IF EXISTS `ledger_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ledger_entries` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `account_id` bigint(20) NOT NULL,
  `transaction_reference` varchar(100) NOT NULL,
  `transaction_type` enum('DEPOSIT','WITHDRAWAL','TRANSFER_DEBIT','TRANSFER_CREDIT','FEE','INTEREST','INTERBANK_DEBIT','INTERBANK_CREDIT','REVERSAL') NOT NULL,
  `debit_amount` decimal(18,2) DEFAULT NULL,
  `credit_amount` decimal(18,2) DEFAULT NULL,
  `balance_after` decimal(18,2) NOT NULL,
  `transaction_date` datetime NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  CONSTRAINT `ledger_entries_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ledger_entries`
--

LOCK TABLES `ledger_entries` WRITE;
/*!40000 ALTER TABLE `ledger_entries` DISABLE KEYS */;
INSERT INTO `ledger_entries` VALUES (1,1,'LDG-1','INTEREST',0.00,31.25,26498.25,'2026-08-27 07:48:11','2026-08-27 07:48:11');
/*!40000 ALTER TABLE `ledger_entries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `roles` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `role_code` varchar(50) NOT NULL,
  `role_name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `role_code` (`role_code`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'ADMIN','System Administrator','Full administrative access to all system resources and audit logs','2026-08-27 07:45:52'),(2,'STAFF','Bank Staff','Operational access to process customer accounts, deposits, and withdrawals','2026-08-27 07:45:52'),(3,'CUSTOMER','Bank Customer','Customer access to personal accounts and fund transfers','2026-08-27 07:45:52');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sessions`
--

DROP TABLE IF EXISTS `sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sessions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `jwt_token` text NOT NULL,
  `refresh_token` text DEFAULT NULL,
  `ip_address` varchar(50) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `login_at` timestamp NULL DEFAULT current_timestamp(),
  `expires_at` datetime NOT NULL,
  `revoked_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sessions`
--

LOCK TABLES `sessions` WRITE;
/*!40000 ALTER TABLE `sessions` DISABLE KEYS */;
INSERT INTO `sessions` VALUES (1,1,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9.dbXIZjk6Uw4fOGFzizBxDeo36k769IsobbKu705xJ8U',NULL,'127.0.0.1','python-requests/2.34.2','2026-08-27 07:47:04','2026-08-27 08:17:04','2026-08-27 07:57:17'),(2,2,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFmZiJ9.UcH0kbL2n2f3S_wxkbWSQ1l0jCv4HRPhSpByxYu_ZLc',NULL,'127.0.0.1','python-requests/2.34.2','2026-08-27 07:47:04','2026-08-27 08:17:04',NULL),(3,3,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjdXN0b21lciJ9.IwFB5mXOIGzIsV92LSo-X8_eRBsf2QIAZbaRawJjla4',NULL,'127.0.0.1','python-requests/2.34.2','2026-08-27 07:47:05','2026-08-27 08:17:05',NULL),(4,1,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9.dbXIZjk6Uw4fOGFzizBxDeo36k769IsobbKu705xJ8U',NULL,'127.0.0.1','python-requests/2.34.2','2026-08-27 07:47:18','2026-08-27 08:17:18',NULL),(5,2,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFmZiJ9.UcH0kbL2n2f3S_wxkbWSQ1l0jCv4HRPhSpByxYu_ZLc',NULL,'127.0.0.1','python-requests/2.34.2','2026-08-27 07:47:18','2026-08-27 08:17:18',NULL),(6,3,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjdXN0b21lciJ9.IwFB5mXOIGzIsV92LSo-X8_eRBsf2QIAZbaRawJjla4',NULL,'127.0.0.1','python-requests/2.34.2','2026-08-27 07:47:18','2026-08-27 08:17:18',NULL),(7,1,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9.dbXIZjk6Uw4fOGFzizBxDeo36k769IsobbKu705xJ8U',NULL,'127.0.0.1','python-requests/2.34.2','2026-08-27 07:47:27','2026-08-27 08:17:27',NULL),(8,2,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFmZiJ9.UcH0kbL2n2f3S_wxkbWSQ1l0jCv4HRPhSpByxYu_ZLc',NULL,'127.0.0.1','python-requests/2.34.2','2026-08-27 07:47:27','2026-08-27 08:17:27',NULL),(9,3,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjdXN0b21lciJ9.IwFB5mXOIGzIsV92LSo-X8_eRBsf2QIAZbaRawJjla4',NULL,'127.0.0.1','python-requests/2.34.2','2026-08-27 07:47:27','2026-08-27 08:17:27',NULL),(10,1,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9.dbXIZjk6Uw4fOGFzizBxDeo36k769IsobbKu705xJ8U',NULL,'127.0.0.1','python-requests/2.34.2','2026-08-27 07:47:37','2026-08-27 08:17:37',NULL),(11,2,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFmZiJ9.UcH0kbL2n2f3S_wxkbWSQ1l0jCv4HRPhSpByxYu_ZLc',NULL,'127.0.0.1','python-requests/2.34.2','2026-08-27 07:47:37','2026-08-27 08:17:37',NULL),(12,3,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjdXN0b21lciJ9.IwFB5mXOIGzIsV92LSo-X8_eRBsf2QIAZbaRawJjla4',NULL,'127.0.0.1','python-requests/2.34.2','2026-08-27 07:47:37','2026-08-27 08:17:37',NULL),(13,1,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9.dbXIZjk6Uw4fOGFzizBxDeo36k769IsobbKu705xJ8U',NULL,'127.0.0.1','python-requests/2.34.2','2026-08-27 07:48:10','2026-08-27 08:18:10',NULL),(14,2,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFmZiJ9.UcH0kbL2n2f3S_wxkbWSQ1l0jCv4HRPhSpByxYu_ZLc',NULL,'127.0.0.1','python-requests/2.34.2','2026-08-27 07:48:10','2026-08-27 08:18:10',NULL),(15,3,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjdXN0b21lciJ9.IwFB5mXOIGzIsV92LSo-X8_eRBsf2QIAZbaRawJjla4',NULL,'127.0.0.1','python-requests/2.34.2','2026-08-27 07:48:10','2026-08-27 08:18:10',NULL);
/*!40000 ALTER TABLE `sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transfers`
--

DROP TABLE IF EXISTS `transfers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transfers` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `source_account_id` bigint(20) NOT NULL,
  `destination_account_id` bigint(20) NOT NULL,
  `transfer_reference` varchar(100) NOT NULL,
  `amount` decimal(18,2) NOT NULL,
  `transfer_type` enum('INTERNAL','SCHEDULED') DEFAULT NULL,
  `remarks` text DEFAULT NULL,
  `status` enum('PENDING','SUCCESS','FAILED','REVERSED') DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `completed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `transfer_reference` (`transfer_reference`),
  KEY `source_account_id` (`source_account_id`),
  KEY `destination_account_id` (`destination_account_id`),
  CONSTRAINT `transfers_ibfk_1` FOREIGN KEY (`source_account_id`) REFERENCES `accounts` (`id`),
  CONSTRAINT `transfers_ibfk_2` FOREIGN KEY (`destination_account_id`) REFERENCES `accounts` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transfers`
--

LOCK TABLES `transfers` WRITE;
/*!40000 ALTER TABLE `transfers` DISABLE KEYS */;
INSERT INTO `transfers` VALUES (1,1,2,'TRF-TEST-1',2000.00,'INTERNAL','Dry-run internal transfer','SUCCESS','2026-08-27 07:48:11','2026-08-27 07:48:11');
/*!40000 ALTER TABLE `transfers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `email` varchar(150) DEFAULT NULL,
  `mobile_number` varchar(30) DEFAULT NULL,
  `first_name` varchar(100) NOT NULL,
  `middle_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `role_id` bigint(20) NOT NULL,
  `account_status` enum('ACTIVE','LOCKED','DISABLED') DEFAULT NULL,
  `last_login_at` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','$2b$12$wNHAAD/NX0ZFG0EotlNRKO.IjpnWPaZYf.Lh5mUHZltyq8I8c0hMm','admin@bank.local',NULL,'System',NULL,'Admin',NULL,1,'ACTIVE','2026-08-27 07:48:10','2026-08-27 07:45:52','2026-08-27 07:48:10'),(2,'staff','$2b$12$UmbbImDViX7B88FHHPuhRuss0x.C9DbEA.ZU2hzTEQsrIFBZKUiAi','staff@bank.local',NULL,'Bank',NULL,'Officer',NULL,2,'ACTIVE','2026-08-27 07:48:10','2026-08-27 07:45:52','2026-08-27 07:48:10'),(3,'customer','$2b$12$sV8dY.xM5YHsVGB71xHkqeTAjHMFfAqMCsXqbR1cCQWfP/fRODDpG','customer@bank.local',NULL,'Juan',NULL,'Dela Cruz',NULL,3,'ACTIVE','2026-08-27 07:48:10','2026-08-27 07:45:52','2026-08-27 07:48:10'),(4,'nexgen','$2b$12$mtvVFInWc3qpy7KwgwUoYeKcGviopWAd0wktMdnhk4O7gKvwkEl4C','nexgentoyongan213@gmail.com','09123456789','nexgen','','toyongan',NULL,2,'ACTIVE',NULL,'2026-08-27 07:53:32','2026-08-27 07:53:32'),(5,'paulszx','$2b$12$DVspWjqdCqivllNlnm8wKuo7AKwHQ50uG3SWfN6r98IBSASPJt0Y6','nexgen@gmail.com','09123456789','nexgen','','toyongan',NULL,1,'ACTIVE',NULL,'2026-08-27 07:54:59','2026-08-27 07:54:59');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `withdrawal_limits`
--

DROP TABLE IF EXISTS `withdrawal_limits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `withdrawal_limits` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `account_id` bigint(20) NOT NULL,
  `daily_limit_amount` decimal(18,2) NOT NULL,
  `daily_used_amount` decimal(18,2) DEFAULT NULL,
  `last_reset_date` date NOT NULL,
  `updated_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `account_id` (`account_id`),
  CONSTRAINT `withdrawal_limits_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `withdrawal_limits`
--

LOCK TABLES `withdrawal_limits` WRITE;
/*!40000 ALTER TABLE `withdrawal_limits` DISABLE KEYS */;
INSERT INTO `withdrawal_limits` VALUES (1,1,50000.00,1000.00,'2026-08-27','2026-08-27 07:48:11');
/*!40000 ALTER TABLE `withdrawal_limits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `withdrawals`
--

DROP TABLE IF EXISTS `withdrawals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `withdrawals` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `account_id` bigint(20) NOT NULL,
  `reference_number` varchar(100) NOT NULL,
  `amount` decimal(18,2) NOT NULL,
  `withdrawal_channel` enum('ATM','ONLINE','BRANCH','INTERBANK') NOT NULL,
  `approved_by_user_id` bigint(20) DEFAULT NULL,
  `remarks` text DEFAULT NULL,
  `transaction_date` datetime NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `reference_number` (`reference_number`),
  KEY `account_id` (`account_id`),
  KEY `approved_by_user_id` (`approved_by_user_id`),
  CONSTRAINT `withdrawals_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  CONSTRAINT `withdrawals_ibfk_2` FOREIGN KEY (`approved_by_user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `withdrawals`
--

LOCK TABLES `withdrawals` WRITE;
/*!40000 ALTER TABLE `withdrawals` DISABLE KEYS */;
INSERT INTO `withdrawals` VALUES (1,1,'WTH-TEST-1',1000.00,'BRANCH',NULL,'Dry-run test withdrawal','2026-08-27 07:48:11','2026-08-27 07:48:11');
/*!40000 ALTER TABLE `withdrawals` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-27 15:59:35
