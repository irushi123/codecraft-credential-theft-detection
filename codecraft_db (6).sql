CREATE DATABASE  IF NOT EXISTS `codecraft_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `codecraft_db`;
-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: codecraft_db
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `User_ID` int NOT NULL,
  `Admin_role` varchar(50) NOT NULL,
  `Approval_status` varchar(20) DEFAULT 'Pending',
  `Is_super_admin` tinyint(1) DEFAULT '0',
  `Otp_code` varchar(6) DEFAULT NULL,
  `Otp_expiry` datetime DEFAULT NULL,
  PRIMARY KEY (`User_ID`),
  CONSTRAINT `admin_ibfk_1` FOREIGN KEY (`User_ID`) REFERENCES `users` (`User_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (2,'SecurityAdmin','Approved',1,NULL,NULL),(10,'SecurityAdmin','Pending',0,NULL,NULL),(11,'SecurityAdmin','Pending',0,NULL,NULL),(12,'SecurityAdmin','Pending',0,NULL,NULL),(13,'SecurityAdmin','Pending',0,NULL,NULL),(14,'SecurityAdmin','Pending',0,NULL,NULL),(15,'SecurityAdmin','Pending',0,NULL,NULL),(17,'SecurityAdmin','Pending',0,NULL,NULL),(18,'SecurityAdmin','Pending',0,NULL,NULL),(19,'SecurityAdmin','OTP_Sent',0,'978491','2026-08-11 17:02:59'),(20,'SecurityAdmin','OTP_Sent',0,'854332','2026-08-11 17:09:34'),(21,'SecurityAdmin','OTP_Sent',0,'885154','2026-08-11 23:53:11'),(23,'SecurityAdmin','Pending',0,NULL,NULL),(25,'SecurityAdmin','OTP_Sent',0,'666414','2026-09-04 21:49:19');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_action`
--

DROP TABLE IF EXISTS `admin_action`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_action` (
  `Action_ID` int NOT NULL AUTO_INCREMENT,
  `Admin_ID` int NOT NULL,
  `Target_User_ID` int NOT NULL,
  `Action_type` varchar(50) NOT NULL,
  `Action_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Action_ID`),
  KEY `Admin_ID` (`Admin_ID`),
  KEY `Target_User_ID` (`Target_User_ID`),
  CONSTRAINT `admin_action_ibfk_1` FOREIGN KEY (`Admin_ID`) REFERENCES `admin` (`User_ID`) ON DELETE CASCADE,
  CONSTRAINT `admin_action_ibfk_2` FOREIGN KEY (`Target_User_ID`) REFERENCES `normal_user` (`User_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_action`
--

LOCK TABLES `admin_action` WRITE;
/*!40000 ALTER TABLE `admin_action` DISABLE KEYS */;
INSERT INTO `admin_action` VALUES (1,2,1,'unlock_account','2026-07-31 09:30:17'),(2,2,1,'unlock_account','2026-07-31 11:00:52'),(3,2,1,'unlock_account','2026-08-02 12:18:02'),(4,2,1,'Mark_False_Positive','2026-08-04 11:21:25'),(5,2,1,'lock_account','2026-08-04 11:21:33'),(6,2,1,'Mark_False_Positive','2026-08-04 11:21:36'),(7,2,1,'unlock_account','2026-08-04 11:21:52'),(8,2,1,'unlock_account','2026-08-04 11:22:06'),(9,2,1,'unlock_account','2026-08-04 12:09:05'),(10,2,1,'Mark_False_Positive','2026-08-04 13:38:52'),(11,2,1,'lock_account','2026-08-04 13:38:55'),(12,2,1,'unlock_account','2026-08-04 13:39:22'),(13,2,1,'lock_account','2026-08-04 14:23:48'),(14,2,1,'Mark_False_Positive','2026-08-04 14:23:51'),(15,2,1,'lock_account','2026-08-04 14:24:06'),(16,2,1,'unlock_account','2026-08-04 14:24:12'),(17,2,1,'Mark_False_Positive','2026-08-04 14:24:28'),(18,2,1,'unlock_account','2026-08-04 14:25:19'),(19,2,1,'lock_account','2026-08-10 11:47:07'),(20,2,1,'lock_account','2026-08-10 11:47:20'),(21,2,1,'unlock_account','2026-08-10 11:55:14'),(22,2,1,'lock_account','2026-08-11 11:21:38'),(23,2,1,'unlock_account','2026-08-11 11:27:10');
/*!40000 ALTER TABLE `admin_action` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_rejection_log`
--

DROP TABLE IF EXISTS `admin_rejection_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_rejection_log` (
  `Rejection_ID` int NOT NULL AUTO_INCREMENT,
  `Rejected_Email` varchar(100) NOT NULL,
  `Rejected_Name` varchar(100) DEFAULT NULL,
  `Reason` text NOT NULL,
  `Rejected_By` int NOT NULL,
  `Rejected_At` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Rejection_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_rejection_log`
--

LOCK TABLES `admin_rejection_log` WRITE;
/*!40000 ALTER TABLE `admin_rejection_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_rejection_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course`
--

DROP TABLE IF EXISTS `course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course` (
  `Course_ID` int NOT NULL AUTO_INCREMENT,
  `Course_name` varchar(100) NOT NULL,
  `Description` text,
  PRIMARY KEY (`Course_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course`
--

LOCK TABLES `course` WRITE;
/*!40000 ALTER TABLE `course` DISABLE KEYS */;
INSERT INTO `course` VALUES (1,'Python Programming','Introduction to Python programming language and problem solving.'),(2,'Data Structures','Fundamental data structures: arrays, linked lists, trees, graphs.'),(3,'Database Systems','Relational database design, SQL, and normalization.'),(4,'Machine Learning','Supervised and unsupervised learning techniques.');
/*!40000 ALTER TABLE `course` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enrollment`
--

DROP TABLE IF EXISTS `enrollment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enrollment` (
  `Enrollment_ID` int NOT NULL AUTO_INCREMENT,
  `User_ID` int NOT NULL,
  `Course_ID` int NOT NULL,
  PRIMARY KEY (`Enrollment_ID`),
  KEY `User_ID` (`User_ID`),
  KEY `Course_ID` (`Course_ID`),
  CONSTRAINT `enrollment_ibfk_1` FOREIGN KEY (`User_ID`) REFERENCES `normal_user` (`User_ID`) ON DELETE CASCADE,
  CONSTRAINT `enrollment_ibfk_2` FOREIGN KEY (`Course_ID`) REFERENCES `course` (`Course_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enrollment`
--

LOCK TABLES `enrollment` WRITE;
/*!40000 ALTER TABLE `enrollment` DISABLE KEYS */;
INSERT INTO `enrollment` VALUES (1,1,1),(2,1,2),(3,1,3),(4,6,1),(5,6,2),(6,6,3),(7,6,4),(8,7,1),(9,7,2),(10,7,3),(11,7,4),(12,8,1),(13,8,2),(14,8,3),(15,8,4),(16,9,1),(17,9,2),(18,9,3),(19,9,4),(20,16,1),(21,16,2),(22,16,3),(23,16,4),(24,22,1),(25,22,2),(26,22,3),(27,22,4),(28,24,1),(29,24,2),(30,24,3),(31,24,4);
/*!40000 ALTER TABLE `enrollment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `explanation`
--

DROP TABLE IF EXISTS `explanation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `explanation` (
  `Explanation_ID` int NOT NULL AUTO_INCREMENT,
  `Risk_ID` int NOT NULL,
  `Explanation_summary` text,
  `Key_factors` text,
  `Confidence_level` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`Explanation_ID`),
  UNIQUE KEY `Risk_ID` (`Risk_ID`),
  CONSTRAINT `explanation_ibfk_1` FOREIGN KEY (`Risk_ID`) REFERENCES `risk_assessment` (`Risk_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=90 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `explanation`
--

LOCK TABLES `explanation` WRITE;
/*!40000 ALTER TABLE `explanation` DISABLE KEYS */;
INSERT INTO `explanation` VALUES (1,2,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',17.99),(2,3,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',17.98),(3,4,'Login attempt analyzed. Key contributing factors: Country_RO','Country_RO',14.87),(4,6,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',17.99),(5,7,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.09),(6,8,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.20),(7,9,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.20),(8,10,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.11),(9,11,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.11),(10,12,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.11),(11,13,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.11),(12,14,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.11),(13,15,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.11),(14,16,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.25),(15,17,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.25),(16,18,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.25),(17,19,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.25),(18,20,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.25),(19,21,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.19),(20,22,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.15),(21,23,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.15),(22,24,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.15),(23,25,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.15),(24,26,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.15),(25,27,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.79),(26,28,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.79),(27,29,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.69),(28,30,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.57),(29,31,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.57),(30,32,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.60),(31,33,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.60),(32,35,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.15),(33,34,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.15),(34,36,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.15),(35,37,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.15),(36,38,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.15),(37,39,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',17.80),(38,40,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',17.80),(39,41,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',17.80),(40,42,'Login attempt analyzed. Key contributing factors: Country_RO','Country_RO',12.37),(41,43,'Login attempt analyzed. Key contributing factors: Country_RO, Device Type_desktop, OS Family_Mac OS','Country_RO, Device Type_desktop, OS Family_Mac OS',17.30),(42,44,'Login attempt analyzed. Key contributing factors: Country_RO, Device Type_desktop, OS Family_Mac OS','Country_RO, Device Type_desktop, OS Family_Mac OS',17.30),(43,45,'Login attempt analyzed. Key contributing factors: Country_RO, Device Type_desktop, OS Family_Mac OS','Country_RO, Device Type_desktop, OS Family_Mac OS',17.30),(44,46,'Login attempt analyzed. Key contributing factors: Country_RO, Device Type_desktop, OS Family_Mac OS','Country_RO, Device Type_desktop, OS Family_Mac OS',17.30),(45,47,'Login attempt analyzed. Key contributing factors: Country_RO, Device Type_desktop, OS Family_Mac OS','Country_RO, Device Type_desktop, OS Family_Mac OS',17.30),(46,48,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.65),(47,49,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.47),(48,50,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.47),(49,51,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.57),(50,52,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.57),(51,53,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.47),(52,54,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.57),(53,55,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',18.57),(54,56,'Login attempt analyzed. Key contributing factors: Country_RO','Country_RO',17.98),(55,57,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.47),(56,58,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.36),(57,59,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.36),(58,60,'Login attempt analyzed. Key contributing factors: Country_RO','Country_RO',18.51),(59,61,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.31),(60,62,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.31),(61,63,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.27),(62,64,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.30),(63,65,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.20),(64,66,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.20),(65,67,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.20),(66,68,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.20),(67,69,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.20),(68,71,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.58),(69,70,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.58),(70,72,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.58),(71,73,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.58),(72,74,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.58),(73,75,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.58),(74,76,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.58),(75,77,'Login attempt analyzed. Key contributing factors: Country_RO','Country_RO',17.68),(76,78,'Login attempt analyzed. Key contributing factors: Country_RO','Country_RO',16.86),(77,79,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.65),(78,80,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.27),(79,81,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.30),(80,82,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.56),(81,83,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.56),(82,84,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.54),(83,85,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.54),(84,86,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',16.54),(85,87,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',17.38),(86,88,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',17.31),(87,89,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',171.01),(88,90,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',162.04),(89,91,'Login attempt analyzed. Key contributing factors: No significant risk factors detected','No significant risk factors detected',162.04);
/*!40000 ALTER TABLE `explanation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback` (
  `Feedback_ID` int NOT NULL AUTO_INCREMENT,
  `User_ID` int NOT NULL,
  `Feedback_text` text NOT NULL,
  `Submitted_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Feedback_ID`),
  KEY `User_ID` (`User_ID`),
  CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`User_ID`) REFERENCES `normal_user` (`User_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feedback`
--

LOCK TABLES `feedback` WRITE;
/*!40000 ALTER TABLE `feedback` DISABLE KEYS */;
INSERT INTO `feedback` VALUES (1,1,'good','2026-08-10 11:24:31');
/*!40000 ALTER TABLE `feedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `login_attempt`
--

DROP TABLE IF EXISTS `login_attempt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `login_attempt` (
  `Login_ID` int NOT NULL AUTO_INCREMENT,
  `User_ID` int NOT NULL,
  `Login_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `IP_address` varchar(45) NOT NULL,
  `User_agent` varchar(255) DEFAULT NULL,
  `Login_status` varchar(20) NOT NULL,
  PRIMARY KEY (`Login_ID`),
  KEY `User_ID` (`User_ID`),
  CONSTRAINT `login_attempt_ibfk_1` FOREIGN KEY (`User_ID`) REFERENCES `normal_user` (`User_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=184 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login_attempt`
--

LOCK TABLES `login_attempt` WRITE;
/*!40000 ALTER TABLE `login_attempt` DISABLE KEYS */;
INSERT INTO `login_attempt` VALUES (1,1,'2026-07-29 14:39:56','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(2,1,'2026-07-29 15:15:28','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(3,1,'2026-07-29 15:28:03','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(4,1,'2026-07-29 16:06:07','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(5,1,'2026-07-29 16:15:41','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(6,1,'2026-07-29 16:42:07','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(7,1,'2026-07-29 17:04:06','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(8,1,'2026-07-31 08:24:10','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(9,1,'2026-07-31 08:28:03','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(10,1,'2026-07-31 08:29:12','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(11,1,'2026-07-31 08:29:27','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(12,1,'2026-07-31 08:30:08','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(13,1,'2026-07-31 08:30:20','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(14,1,'2026-07-31 09:12:11','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(15,1,'2026-07-31 09:28:57','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(16,1,'2026-07-31 09:29:08','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(17,1,'2026-07-31 09:29:17','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(18,1,'2026-07-31 09:29:24','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(19,1,'2026-07-31 09:29:32','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(20,1,'2026-07-31 09:30:31','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(21,1,'2026-07-31 10:07:25','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(22,1,'2026-07-31 10:15:04','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(23,1,'2026-07-31 10:30:32','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(24,1,'2026-07-31 10:30:38','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(25,1,'2026-07-31 10:55:24','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(26,1,'2026-07-31 10:57:08','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(27,1,'2026-07-31 10:58:28','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(28,1,'2026-07-31 10:58:46','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(29,1,'2026-07-31 10:58:55','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(30,1,'2026-07-31 10:59:03','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(31,1,'2026-07-31 10:59:09','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(32,1,'2026-07-31 11:16:38','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(33,5,'2026-07-31 11:18:10','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(34,1,'2026-07-31 11:19:13','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(35,6,'2026-07-31 11:27:17','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(36,7,'2026-07-31 11:28:21','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(37,8,'2026-07-31 11:59:59','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(38,9,'2026-07-31 12:21:12','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(51,1,'2026-07-31 14:06:35','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(53,1,'2026-07-31 14:18:06','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(54,1,'2026-07-31 14:24:45','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(55,1,'2026-07-31 14:33:36','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(56,1,'2026-07-31 14:45:40','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(57,1,'2026-08-02 11:22:46','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(58,1,'2026-08-02 11:32:08','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(59,1,'2026-08-02 12:11:36','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(60,1,'2026-08-02 12:16:42','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(61,1,'2026-08-02 12:16:53','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(62,1,'2026-08-02 12:17:01','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(63,1,'2026-08-02 12:17:09','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(64,1,'2026-08-02 12:17:18','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(65,1,'2026-08-02 15:05:22','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(66,16,'2026-08-02 15:07:06','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(67,1,'2026-08-02 16:23:48','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(68,16,'2026-08-02 16:25:40','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(69,1,'2026-08-03 14:00:57','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(70,1,'2026-08-03 14:00:59','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(71,1,'2026-08-03 14:06:04','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(72,1,'2026-08-03 14:09:14','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(73,1,'2026-08-03 14:20:18','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(74,1,'2026-08-03 20:14:42','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(75,1,'2026-08-03 20:18:38','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(76,1,'2026-08-03 20:47:02','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(77,1,'2026-08-04 10:30:34','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(78,1,'2026-08-04 11:19:51','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(79,16,'2026-08-04 11:23:17','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(80,1,'2026-08-04 11:31:40','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(81,1,'2026-08-04 11:36:11','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(82,1,'2026-08-04 11:36:20','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(83,1,'2026-08-04 11:56:32','10.40.4.176','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(84,1,'2026-08-04 12:06:16','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(85,1,'2026-08-04 12:07:46','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(86,1,'2026-08-04 12:07:58','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(87,1,'2026-08-04 12:08:09','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(88,1,'2026-08-04 12:08:16','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(89,1,'2026-08-04 12:08:24','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(90,1,'2026-08-04 12:09:18','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(91,1,'2026-08-04 12:23:40','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(92,1,'2026-08-04 12:24:11','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(93,1,'2026-08-04 12:24:24','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(94,1,'2026-08-04 12:24:32','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(95,1,'2026-08-04 12:24:53','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(96,1,'2026-08-04 12:25:02','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(97,1,'2026-08-04 12:25:10','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(98,1,'2026-08-04 12:25:19','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(99,1,'2026-08-04 12:31:04','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(100,1,'2026-08-04 12:31:33','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(101,1,'2026-08-04 12:31:56','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(102,1,'2026-08-04 12:32:02','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(103,1,'2026-08-04 12:32:11','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(104,1,'2026-08-04 12:32:53','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(105,1,'2026-08-04 12:33:01','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(106,1,'2026-08-04 12:33:07','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(107,1,'2026-08-04 12:33:15','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(108,1,'2026-08-04 12:49:55','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(109,1,'2026-08-04 12:50:12','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(110,1,'2026-08-04 12:50:20','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(111,1,'2026-08-04 12:50:27','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(112,1,'2026-08-04 12:50:45','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(113,1,'2026-08-04 13:37:01','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(114,1,'2026-08-04 13:39:46','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(115,1,'2026-08-04 14:22:23','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(116,1,'2026-08-04 14:22:40','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(117,1,'2026-08-04 14:22:48','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(118,1,'2026-08-04 14:22:56','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(119,1,'2026-08-04 14:23:04','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(120,1,'2026-08-04 14:24:43','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(121,1,'2026-08-04 14:25:38','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(122,1,'2026-08-04 14:33:27','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(123,1,'2026-08-04 14:49:45','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(124,1,'2026-08-04 16:10:09','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(125,1,'2026-08-04 17:34:06','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(126,1,'2026-08-04 18:07:08','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(127,1,'2026-08-04 18:07:16','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(128,1,'2026-08-04 18:07:24','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(129,1,'2026-08-04 18:07:33','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(130,1,'2026-08-04 18:07:43','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(131,16,'2026-08-04 18:08:57','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(132,16,'2026-08-04 18:09:13','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(133,16,'2026-08-04 18:09:25','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(134,16,'2026-08-04 18:09:42','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Failed'),(135,16,'2026-08-04 18:10:07','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(136,1,'2026-08-04 18:18:16','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(137,1,'2026-08-04 18:20:37','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(138,1,'2026-08-04 18:22:11','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36','Success'),(139,1,'2026-08-10 11:23:53','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(140,1,'2026-08-10 11:23:56','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(141,1,'2026-08-10 11:29:17','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(142,1,'2026-08-10 11:55:34','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Failed'),(143,1,'2026-08-10 11:55:51','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Failed'),(144,1,'2026-08-10 11:56:01','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Failed'),(145,1,'2026-08-10 11:56:08','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Failed'),(146,1,'2026-08-10 11:56:17','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(147,1,'2026-08-10 11:56:28','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(148,1,'2026-08-10 11:56:41','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(149,16,'2026-08-10 11:57:33','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Failed'),(150,16,'2026-08-10 11:57:54','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Failed'),(151,16,'2026-08-10 11:58:11','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(152,1,'2026-08-10 12:15:11','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Failed'),(153,1,'2026-08-10 12:15:19','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Failed'),(154,1,'2026-08-10 12:15:29','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(155,16,'2026-08-10 12:16:05','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Failed'),(156,16,'2026-08-10 12:16:18','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Failed'),(157,16,'2026-08-10 12:16:25','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Failed'),(158,16,'2026-08-10 12:16:33','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Failed'),(159,16,'2026-08-10 12:17:02','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(160,1,'2026-08-11 11:07:16','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(161,1,'2026-08-11 16:13:10','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(162,1,'2026-08-11 17:03:02','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(163,1,'2026-08-11 22:07:53','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(164,1,'2026-08-11 22:14:38','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(165,1,'2026-08-11 23:01:51','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(166,1,'2026-08-11 23:07:32','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(167,1,'2026-08-11 23:12:23','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Failed'),(168,1,'2026-08-11 23:12:54','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(169,1,'2026-08-12 09:42:40','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(170,22,'2026-08-12 11:09:28','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36','Success'),(171,24,'2026-09-04 21:06:56','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36','Success'),(172,1,'2026-09-04 21:07:42','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36','Failed'),(173,1,'2026-09-04 21:08:02','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36','Failed'),(174,24,'2026-09-04 21:08:37','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36','Failed'),(175,24,'2026-09-04 21:08:55','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36','Success'),(176,24,'2026-09-04 21:18:00','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36','Failed'),(177,24,'2026-09-04 21:18:17','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36','Success'),(178,24,'2026-09-04 21:32:48','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36','Failed'),(179,24,'2026-09-04 21:33:00','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36','Failed'),(180,24,'2026-09-04 21:33:12','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36','Success'),(181,1,'2026-09-09 14:27:53','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36','Success'),(182,1,'2026-09-09 14:29:36','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36','Failed'),(183,1,'2026-09-09 14:29:50','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36','Success');
/*!40000 ALTER TABLE `login_attempt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `normal_user`
--

DROP TABLE IF EXISTS `normal_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `normal_user` (
  `User_ID` int NOT NULL,
  PRIMARY KEY (`User_ID`),
  CONSTRAINT `normal_user_ibfk_1` FOREIGN KEY (`User_ID`) REFERENCES `users` (`User_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `normal_user`
--

LOCK TABLES `normal_user` WRITE;
/*!40000 ALTER TABLE `normal_user` DISABLE KEYS */;
INSERT INTO `normal_user` VALUES (1),(3),(4),(5),(6),(7),(8),(9),(16),(22),(24);
/*!40000 ALTER TABLE `normal_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `risk_assessment`
--

DROP TABLE IF EXISTS `risk_assessment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `risk_assessment` (
  `Risk_ID` int NOT NULL AUTO_INCREMENT,
  `Login_ID` int NOT NULL,
  `Risk_score` decimal(5,2) NOT NULL,
  `Risk_level` varchar(20) NOT NULL,
  `Assessed_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Risk_ID`),
  UNIQUE KEY `Login_ID` (`Login_ID`),
  CONSTRAINT `risk_assessment_ibfk_1` FOREIGN KEY (`Login_ID`) REFERENCES `login_attempt` (`Login_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=92 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `risk_assessment`
--

LOCK TABLES `risk_assessment` WRITE;
/*!40000 ALTER TABLE `risk_assessment` DISABLE KEYS */;
INSERT INTO `risk_assessment` VALUES (1,2,7.50,'Low','2026-07-29 15:15:30'),(2,3,7.50,'Low','2026-07-29 15:28:04'),(3,4,7.50,'Low','2026-07-29 16:06:07'),(4,5,20.50,'Low','2026-07-29 16:15:41'),(5,6,7.50,'Low','2026-07-29 16:42:07'),(6,7,7.50,'Low','2026-07-29 17:04:07'),(7,8,7.00,'Low','2026-07-31 08:24:12'),(8,14,7.00,'Low','2026-07-31 09:12:12'),(9,20,7.00,'Low','2026-07-31 09:30:31'),(10,21,7.00,'Low','2026-07-31 10:07:25'),(11,22,7.00,'Low','2026-07-31 10:15:04'),(12,23,7.00,'Low','2026-07-31 10:30:32'),(13,24,7.00,'Low','2026-07-31 10:30:38'),(14,25,7.00,'Low','2026-07-31 10:55:25'),(15,26,7.00,'Low','2026-07-31 10:57:08'),(16,32,7.00,'Low','2026-07-31 11:16:39'),(17,33,7.00,'Low','2026-07-31 11:18:11'),(18,34,7.00,'Low','2026-07-31 11:19:13'),(19,36,7.00,'Low','2026-07-31 11:28:21'),(20,37,7.00,'Low','2026-07-31 12:00:00'),(21,38,7.00,'Low','2026-07-31 12:21:12'),(22,51,7.50,'Low','2026-07-31 14:06:39'),(23,53,7.50,'Low','2026-07-31 14:18:06'),(24,54,7.50,'Low','2026-07-31 14:24:46'),(25,55,7.50,'Low','2026-07-31 14:33:37'),(26,56,7.50,'Low','2026-07-31 14:45:40'),(27,57,10.50,'Low','2026-08-02 11:22:47'),(28,58,10.50,'Low','2026-08-02 11:32:08'),(29,59,11.00,'Low','2026-08-02 12:11:36'),(30,65,11.50,'Low','2026-08-02 15:05:38'),(31,66,11.50,'Low','2026-08-02 15:07:06'),(32,67,11.50,'Low','2026-08-02 16:23:49'),(33,68,11.50,'Low','2026-08-02 16:25:40'),(34,69,7.50,'Low','2026-08-03 14:01:04'),(35,70,7.50,'Low','2026-08-03 14:01:04'),(36,71,7.50,'Low','2026-08-03 14:06:04'),(37,72,7.50,'Low','2026-08-03 14:09:15'),(38,73,7.50,'Low','2026-08-03 14:20:18'),(39,74,8.50,'Low','2026-08-03 20:14:42'),(40,75,8.50,'Low','2026-08-03 20:18:38'),(41,76,8.50,'Low','2026-08-03 20:47:20'),(42,77,10.00,'Low','2026-08-04 10:30:48'),(43,78,100.00,'High','2026-08-04 11:20:05'),(44,79,100.00,'High','2026-08-04 11:23:18'),(45,80,100.00,'High','2026-08-04 11:31:40'),(46,81,100.00,'High','2026-08-04 11:36:11'),(47,82,100.00,'High','2026-08-04 11:36:20'),(48,83,2.00,'Low','2026-08-04 11:56:33'),(49,84,2.50,'Low','2026-08-04 12:06:33'),(50,90,2.50,'Low','2026-08-04 12:09:18'),(51,94,7.00,'Low','2026-08-04 12:24:32'),(52,98,7.00,'Low','2026-08-04 12:25:20'),(53,99,2.50,'Low','2026-08-04 12:31:05'),(54,103,7.00,'Low','2026-08-04 12:32:11'),(55,107,7.00,'Low','2026-08-04 12:33:15'),(56,111,66.00,'Medium','2026-08-04 12:50:28'),(57,112,2.50,'Low','2026-08-04 12:50:45'),(58,113,1.00,'Low','2026-08-04 13:37:03'),(59,114,1.00,'Low','2026-08-04 13:39:46'),(60,121,64.00,'Medium','2026-08-04 14:25:47'),(61,122,1.00,'Low','2026-08-04 14:33:28'),(62,123,1.00,'Low','2026-08-04 14:49:52'),(63,124,1.00,'Low','2026-08-04 16:10:10'),(64,125,1.00,'Low','2026-08-04 17:34:07'),(65,130,1.00,'Low','2026-08-04 18:07:48'),(66,135,1.00,'Low','2026-08-04 18:10:08'),(67,136,1.00,'Low','2026-08-04 18:18:16'),(68,137,1.00,'Low','2026-08-04 18:20:37'),(69,138,1.00,'Low','2026-08-04 18:22:12'),(70,139,2.50,'Low','2026-08-10 11:23:56'),(71,140,2.50,'Low','2026-08-10 11:23:56'),(72,141,2.50,'Low','2026-08-10 11:29:22'),(73,146,2.50,'Low','2026-08-10 11:56:37'),(74,147,2.50,'Low','2026-08-10 11:56:38'),(75,148,2.50,'Low','2026-08-10 11:56:42'),(76,151,2.50,'Low','2026-08-10 11:58:12'),(77,154,33.50,'Medium','2026-08-10 12:15:30'),(78,159,43.50,'Medium','2026-08-10 12:17:03'),(79,160,2.00,'Low','2026-08-11 11:07:27'),(80,161,1.00,'Low','2026-08-11 16:13:20'),(81,162,1.00,'Low','2026-08-11 17:03:03'),(82,163,1.00,'Low','2026-08-11 22:07:54'),(83,164,1.00,'Low','2026-08-11 22:14:38'),(84,165,1.00,'Low','2026-08-11 23:01:59'),(85,166,1.00,'Low','2026-08-11 23:07:32'),(86,168,1.00,'Low','2026-08-11 23:12:55'),(87,169,2.00,'Low','2026-08-12 09:42:41'),(88,170,2.00,'Low','2026-08-12 11:09:29'),(89,180,0.78,'Low','2026-09-04 21:33:12'),(90,181,0.26,'Low','2026-09-09 14:28:01'),(91,183,0.26,'Low','2026-09-09 14:29:51');
/*!40000 ALTER TABLE `risk_assessment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `security_alert`
--

DROP TABLE IF EXISTS `security_alert`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `security_alert` (
  `Alert_ID` int NOT NULL AUTO_INCREMENT,
  `Risk_ID` int NOT NULL,
  `Alert_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `Alert_message` text,
  `Alert_status` varchar(20) DEFAULT 'Pending',
  PRIMARY KEY (`Alert_ID`),
  KEY `Risk_ID` (`Risk_ID`),
  CONSTRAINT `security_alert_ibfk_1` FOREIGN KEY (`Risk_ID`) REFERENCES `risk_assessment` (`Risk_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `security_alert`
--

LOCK TABLES `security_alert` WRITE;
/*!40000 ALTER TABLE `security_alert` DISABLE KEYS */;
INSERT INTO `security_alert` VALUES (1,43,'2026-08-04 11:20:07','High Risk Login Detected - example@gmail.com (Risk 100.0%)','Resolved'),(2,44,'2026-08-04 11:23:18','High Risk Login Detected - kasuni333@gmail.com (Risk 100.0%)','Pending'),(3,45,'2026-08-04 11:31:40','High Risk Login Detected - example@gmail.com (Risk 100.0%)','Pending'),(4,46,'2026-08-04 11:36:12','High Risk Login Detected - example@gmail.com (Risk 100.0%)','Pending'),(5,47,'2026-08-04 11:36:20','High Risk Login Detected - example@gmail.com (Risk 100.0%)','Resolved');
/*!40000 ALTER TABLE `security_alert` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `User_ID` int NOT NULL AUTO_INCREMENT,
  `First_name` varchar(50) NOT NULL,
  `Last_name` varchar(50) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `Password` varchar(255) NOT NULL,
  `Created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `Account_status` varchar(20) DEFAULT 'Active',
  `Profile_image` varchar(255) DEFAULT NULL,
  `Password_Reset_OTP` varchar(10) DEFAULT NULL,
  `Password_Reset_Expiry` datetime DEFAULT NULL,
  PRIMARY KEY (`User_ID`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'example','N/A','example@gmail.com','scrypt:32768:8:1$NOzs7iUuJ69ZVMHw$e04c4f4920d63d9b04637eec21b3d0dbdf95d5be253fc94cd96c6b8a21f50f4c4cdd9b0b87ec68311df9a2bae8a72d20ffaf7dfa2f47c6f9fd3419b4731d8dc1','2026-07-29 14:23:55','Active','user_1_profile.jpg','120367','2026-08-12 11:27:52'),(2,'Admin','User','admin@codecraft.com','scrypt:32768:8:1$9tvyghdBKqkvFTgB$9b109634264cc52997de9ac391fc0d0c2fbe7765d9d0a8d8c740c970b91a51625bc96965e291ed2a318e793201e63167cf043bb42b7c52a5b54784409936826d','2026-07-29 17:18:07','Active',NULL,NULL,NULL),(3,'New Student','N/A','newstudent@gmail.com','scrypt:32768:8:1$2udLQxTKLyYPxFMP$2a7f387cf6a3f7c5e28b76a42895a81db7a0b72633b4b21bbb41a329108733434afba4dcd9e0b52ab316732055e00bfde76c078312bd03455c96b829a5b580b6','2026-07-31 09:37:53','Active',NULL,NULL,NULL),(4,'sachi','N/A','sachi1111@gmail.com','scrypt:32768:8:1$yRX2zDb9PWW56kXy$be90af506ec4cb7e737e2903240376d57eaf515acbb39d58c54e7bff6c359cff32ff845f49e2c891763f484b380ab0f2c7eb29968c628bb4ed324b77c4f947db','2026-07-31 10:08:33','Active',NULL,NULL,NULL),(5,'tharu','N/A','tharu112@gmail.com','scrypt:32768:8:1$dndITpj9fDmn8kNf$c9e5c405a911dac9f113ac02d74c2aa5663784a5bf78850fd3054fe3cf96af18be283f0886ee59c34abd7e936f8c6711229a44883252c92ad3f7b6dd48594702','2026-07-31 11:17:54','Active',NULL,NULL,NULL),(6,'kavi','N/A','kavi114@gmail.com','scrypt:32768:8:1$gLICwQgzoNcwP79p$73882ebdeae3a3e24561224b045a67d92c3126bc0cc3b720ab1f1b58b3d6e0d501148f08a6772c2ae2e4053a4063b7689f28c8cbd03889fca42104c6f6d5f2d5','2026-07-31 11:26:47','Active',NULL,NULL,NULL),(7,'malki','N/A','malki333@gmail.com','scrypt:32768:8:1$F6uwiz10CR83N0e8$3e16d00799d7dd7c19c67cc640f51b4aafc1f9e5c6ed57c38ded6f73b2b75e0940b8435de4d7550e31bd7ad188d6e8ef6f8ec8fab83180996564e2579feaaa4e','2026-07-31 11:28:02','Active',NULL,NULL,NULL),(8,'randi','N/A','randi111@gmail.com','scrypt:32768:8:1$7C7YGJbeIifqMuod$5944771090767d6c4493233b7c2ad9c3a9fc6d39ba371ddfbc68d03d40947037d30cc22c67a060bc40a37e2171ed700e0e17e188e409f3bbde1b6b38eba48187','2026-07-31 11:57:43','Active',NULL,NULL,NULL),(9,'dilki','N/A','dilki345@gmail.com','scrypt:32768:8:1$nsj6RC7Da2vQxOHX$30713a3f4b0767ef706202802f84d20850e88e7bd65001c87a0d20e361e9037f5a298a06a579b39714e790e730b096acb04dfbae623d9c0b3bc167cadb7ffde4','2026-07-31 12:20:43','Active',NULL,NULL,NULL),(10,'thilina','N/A','thilina@gmail.com','scrypt:32768:8:1$SSecUz3THN0xUgO6$84b0a2984db68a8ed1166cbf0c4a528e3350b36adf00282d15018c2cec7456e876a828929aa4b9ebf8de94f58ef14e1cdc6fdd8bff262fa503930667e665c378','2026-07-31 12:22:10','Active',NULL,NULL,NULL),(11,'lahiru','N/A','lahiru222@gmail.com','scrypt:32768:8:1$p7roEHA2EErwK7LM$3f73aff46b529d4f5503a3afc58f953750f04dce091860e379b3e7181bf4f2180129639c2ab888ee08e160803088eca06f81baca3c0376bf2f073947852a590f','2026-07-31 12:26:12','Active',NULL,NULL,NULL),(12,'rashi','N/A','rashi222@gmail.com','scrypt:32768:8:1$E2cBmK1A3Q6TXp9m$b9c8a0c87f9fb1e4fcf1359bce5dad2051b668fccaaec08422ec3576ea8a35cc450232a1720dda12649869daa6ca8c1ccbaf3c4d933a82f4d9176c39ef59c5ac','2026-07-31 12:46:06','Active',NULL,NULL,NULL),(13,'sadun','N/A','sadun234@gmail.com','scrypt:32768:8:1$GqI8KXd7NVGp023y$748e0c5c8aec5f540fce361aaef2feba8696f84887e102aa333f6329f74e95f6aadf791ffeac4e89d3f17360f2efcd3a246e8c7d3e798c78c800e881e5378d88','2026-07-31 14:23:25','Active',NULL,NULL,NULL),(14,'ravi','N/A','ravidi222@gmail.com','scrypt:32768:8:1$HFKPoCyNcyiJb8TE$9240c2dc3f91bca9d84ebfa4202410f96979b779018a7aadad33504b48c9f5e09d8c4bf2df5374e3ff40305a26437e424e7e9f79b749806ccf0be04dd223b169','2026-07-31 14:48:11','Active',NULL,NULL,NULL),(15,'saduni','N/A','saduni222@gmail.com','scrypt:32768:8:1$cMozyRBBWucFaTqu$30914d241e350b8e7cf020bf70694de33d29fe767968032962cab4737ffa1a671596964cc8bc923eca108cdb5eec09e6de64b72a13663c1a7c7888914970c3aa','2026-08-02 12:19:53','Active',NULL,NULL,NULL),(16,'kasuni','N/A','kasuni333@gmail.com','scrypt:32768:8:1$0WoBRk0wSjbFaTAo$742dba1ab51856fd14cf25f0bebc2e2d3f57f1073acc628198cf58d146e3475981bbcf2249bc2a7b14bbdfd7970c8f2f920f7829a6fe11cee28eaca07438559e','2026-08-02 15:06:42','Active',NULL,NULL,NULL),(17,'new admin','N/A','newadmin001@gmail.com','scrypt:32768:8:1$85yWmOHnQU9HzYmx$b2f4d4b854837103464b169c3fe0d9e02628a30e02f286babde0c2f0d9b13e043541655a67d61bcdec2ed601157c38d70f21d58497c8a5854b3a44ee6909ccfa','2026-08-11 15:28:15','Active',NULL,NULL,NULL),(18,'sampath','N/A','sampath001@gmail.com','scrypt:32768:8:1$OkZ07KIvUpJN6e1w$e94acf6b13534a5bdf1c6226e3243754c5bc332fb0773d00d139557a2e43efc81b07957257fd1dcfc54979f61fcce330db56372cbe0065d13b42151e05d427ff','2026-08-11 16:16:38','Active',NULL,NULL,NULL),(19,'sadun','N/A','sadun2000@gmail.com','scrypt:32768:8:1$sor9Qolux6Iqjkak$c415401b6599420669e3cb13f79dca2acd36a56df056838267f3e9c77e99726669e761a4e7d2ff5be6817fcf5d5427996ebfcee9beb2ca3918c92abf2961a538','2026-08-11 16:43:29','Active',NULL,NULL,NULL),(20,'monali','N/A','dissanayakemonali72@gmail.com','scrypt:32768:8:1$PAQCE4g2CRPYp9dt$1946f7d064ae459b3bf2dd33d4554aba6dc011a026194c38e1b1483fddd5307d3da28cf9485e5b8574651e89b6a8fa2cc4b4ce8c7a54934dfc5e54d226b579d6','2026-08-11 16:58:50','Active',NULL,NULL,NULL),(21,'dilmi','N/A','dilmi004@gmail.com','scrypt:32768:8:1$paASIuRaAwAxwZk7$23f9b2726ab5f5fec6ec7ed0e3a661db78fa38dc5b7312fec33943b9adb1bac64949485f8b29e041e7bb2aa4eb913dd3d6a741c768cf4cc03d0240677deb7cfd','2026-08-11 23:42:30','Active',NULL,NULL,NULL),(22,'kalani','N/A','kalani004@gmail.com','scrypt:32768:8:1$mr6VEm2sfadbknP1$255629bd866924c9d74d9d4696f77755637ea58750eff210676b92d30d37352134d9cca477a72e8147482ea72298a916a167c0e0c75b6ce34f609caf0e0f386d','2026-08-12 11:08:59','Active','user_22_profile.jpg',NULL,NULL),(23,'ravidu','N/A','ravidu004@gmail.com','scrypt:32768:8:1$rIA978zNE4kVoMan$3993d1c09b28743c0d9bdaa78599c350a6456b920ffa3335d5781ff40b0400b21cb8a99ab51596cd38ef42ae56677d3252d1b5fdf7986bfd7a5d661a57797a58','2026-08-12 11:13:48','Active',NULL,NULL,NULL),(24,'sachini','N/A','sachini113@rjt.ac.lk','scrypt:32768:8:1$bNhacqJXwOfXgcYG$3949dfff35835e5eadb7897e9e1bc939c3e242a314740285daa153ba27844fa3c0f90fb1b21e505bc98a76436d58b8db942b7ee171db2fc62603beca1c0ae4ec','2026-09-04 21:06:28','Active',NULL,NULL,NULL),(25,'yasho','N/A','yasho123@gmail.com','scrypt:32768:8:1$LF57hKHQbY7iGciu$841007c9f144565b38b8ae02b3edb92a5836bf44cf6b65117895124b49c5d6d57ab2c3fa73d0185b6852ab8ee3775ac4965ebf06a2281e67da4365a9752d83b2','2026-09-04 21:38:35','Active',NULL,NULL,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'codecraft_db'
--

--
-- Dumping routines for database 'codecraft_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-09 20:54:05
