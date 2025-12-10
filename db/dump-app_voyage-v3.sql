-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: Instravel
-- ------------------------------------------------------
-- Server version	8.0.43-0ubuntu0.22.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `Instravel`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `Instravel` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `Instravel`;

--
-- Table structure for table `abonnement`
--

DROP TABLE IF EXISTS `abonnement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `abonnement` (
  `id_user1` int NOT NULL,
  `id_user2` int NOT NULL,
  KEY `id_user1` (`id_user1`),
  KEY `id_user2` (`id_user2`),
  CONSTRAINT `abonnement_ibfk_1` FOREIGN KEY (`id_user1`) REFERENCES `users` (`id_user`),
  CONSTRAINT `abonnement_ibfk_2` FOREIGN KEY (`id_user2`) REFERENCES `users` (`id_user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `accomp`
--

DROP TABLE IF EXISTS `accomp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accomp` (
  `id_user` int NOT NULL,
  `id_voyage` int NOT NULL,
  KEY `id_user` (`id_user`),
  KEY `id_voyage` (`id_voyage`),
  CONSTRAINT `accomp_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`),
  CONSTRAINT `accomp_ibfk_2` FOREIGN KEY (`id_voyage`) REFERENCES `voyages` (`id_voyage`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `comm_hashtag`
--

DROP TABLE IF EXISTS `comm_hashtag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comm_hashtag` (
  `id_comm` int NOT NULL,
  `id_hashtag` int NOT NULL,
  KEY `id_comm` (`id_comm`),
  KEY `id_hashtag` (`id_hashtag`),
  CONSTRAINT `comm_hashtag_ibfk_1` FOREIGN KEY (`id_comm`) REFERENCES `commentaires` (`id_comm`),
  CONSTRAINT `comm_hashtag_ibfk_2` FOREIGN KEY (`id_hashtag`) REFERENCES `hashtag` (`id_hashtag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `commentaires`
--

DROP TABLE IF EXISTS `commentaires`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `commentaires` (
  `id_comm` int NOT NULL AUTO_INCREMENT,
  `commentaire` longtext NOT NULL,
  `date_comm` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `id_user` int NOT NULL,
  `id_etape` int NOT NULL,
  `id_hashtag` int DEFAULT NULL,
  PRIMARY KEY (`id_comm`),
  KEY `id_user` (`id_user`),
  KEY `id_etape` (`id_etape`),
  KEY `id_hashtag` (`id_hashtag`),
  CONSTRAINT `commentaires_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`),
  CONSTRAINT `commentaires_ibfk_2` FOREIGN KEY (`id_etape`) REFERENCES `etapes` (`id_etape`),
  CONSTRAINT `commentaires_ibfk_3` FOREIGN KEY (`id_hashtag`) REFERENCES `hashtag` (`id_hashtag`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `etape_hashtag`
--

DROP TABLE IF EXISTS `etape_hashtag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `etape_hashtag` (
  `id_etape` int NOT NULL,
  `id_hashtag` int NOT NULL,
  KEY `id_etape` (`id_etape`),
  KEY `id_hashtag` (`id_hashtag`),
  CONSTRAINT `etape_hashtag_ibfk_1` FOREIGN KEY (`id_etape`) REFERENCES `etapes` (`id_etape`),
  CONSTRAINT `etape_hashtag_ibfk_2` FOREIGN KEY (`id_hashtag`) REFERENCES `hashtag` (`id_hashtag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `etapes`
--

DROP TABLE IF EXISTS `etapes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `etapes` (
  `id_etape` int NOT NULL AUTO_INCREMENT,
  `nom_etape` varchar(50) NOT NULL,
  `date_etape` date NOT NULL DEFAULT (curdate()),
  `description` longtext,
  `localisation` varchar(50) DEFAULT NULL,
  `nb_commentaire` int DEFAULT NULL,
  `nb_like` int DEFAULT NULL,
  `id_voyage` int NOT NULL,
  PRIMARY KEY (`id_etape`),
  KEY `id_voyage` (`id_voyage`),
  CONSTRAINT `etapes_ibfk_1` FOREIGN KEY (`id_voyage`) REFERENCES `voyages` (`id_voyage`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hashtag`
--

DROP TABLE IF EXISTS `hashtag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hashtag` (
  `id_hashtag` int NOT NULL AUTO_INCREMENT,
  `nom_hashtag` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id_hashtag`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `likes`
--

DROP TABLE IF EXISTS `likes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `likes` (
  `id_like` int NOT NULL AUTO_INCREMENT,
  `id_user` int NOT NULL,
  `id_etape` int NOT NULL,
  PRIMARY KEY (`id_like`),
  KEY `id_user` (`id_user`),
  KEY `id_etape` (`id_etape`),
  CONSTRAINT `likes_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`),
  CONSTRAINT `likes_ibfk_2` FOREIGN KEY (`id_etape`) REFERENCES `etapes` (`id_etape`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `photos`
--

DROP TABLE IF EXISTS `photos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `photos` (
  `id_photo` int NOT NULL AUTO_INCREMENT,
  `photo` longblob,
  `id_etape` int NOT NULL,
  PRIMARY KEY (`id_photo`),
  KEY `id_etape` (`id_etape`),
  CONSTRAINT `photos_ibfk_1` FOREIGN KEY (`id_etape`) REFERENCES `etapes` (`id_etape`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id_user` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `mail` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `biographie` text,
  `nationalité` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `photo` longblob,
  `status` varchar(15) DEFAULT 'public',
  `password` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id_user`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `voyages`
--

DROP TABLE IF EXISTS `voyages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `voyages` (
  `id_voyage` int NOT NULL AUTO_INCREMENT,
  `nom_voyage` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `date_départ` date NOT NULL DEFAULT (curdate()),
  `date_arrivée` date DEFAULT NULL,
  `id_user` int NOT NULL,
  PRIMARY KEY (`id_voyage`),
  KEY `id_user` (`id_user`),
  CONSTRAINT `voyages_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-24  0:00:08
