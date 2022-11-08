-- phpMyAdmin SQL Dump
-- version 4.9.5deb2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Oct 31, 2022 at 03:07 AM
-- Server version: 8.0.30-0ubuntu0.20.04.2
-- PHP Version: 7.4.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `manager`
--

-- --------------------------------------------------------

--
-- Table structure for table `companies`
--

CREATE TABLE `companies` (
  `ID` int UNSIGNED NOT NULL,
  `uuid` char(36) NOT NULL,
  `name` tinytext NOT NULL,
  `code` char(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `passwords`
--

CREATE TABLE `passwords` (
  `ID` int UNSIGNED NOT NULL,
  `savedPassword` text NOT NULL,
  `uuid` char(36) NOT NULL,
  `userUUID` char(36) NOT NULL,
  `isKey` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `passwords`
--

INSERT INTO `passwords` (`ID`, `savedPassword`, `uuid`, `userUUID`, `isKey`) VALUES
(1, 'Password123', 'b2857756-37ca-48a0-9aa5-94352ed95670', '51ad9137-a36e-4b12-b462-bcd24b8b47cc', 0),
(2, 'Password321', 'f905cc96-6035-43e4-b8ae-251a72936132', '51ad9137-a36e-4b12-b462-bcd24b8b47cc', 0);

-- --------------------------------------------------------

--
-- Table structure for table `passwordsInfo`
--

CREATE TABLE `passwordsInfo` (
  `ID` int UNSIGNED NOT NULL,
  `passUUID` char(36) NOT NULL,
  `name` tinytext NOT NULL,
  `username` tinytext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `creationDate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `pageURL` tinytext,
  `note` tinytext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `passwordsInfo`
--

INSERT INTO `passwordsInfo` (`ID`, `passUUID`, `name`, `username`, `creationDate`, `pageURL`, `note`) VALUES
(1, 'b2857756-37ca-48a0-9aa5-94352ed95670', 'Pass1', 'admin', '2022-10-24 00:25:56', 'https://www.test.com', 'Lorem ipsum zażółć gęślą jaźń, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi'),
(2, 'f905cc96-6035-43e4-b8ae-251a72936132', 'Pass2', '---', '2022-10-24 00:28:43', 'https://www.test.com', 'Lorem ipsum zażółć gęślą jaźń, consectetur adipiscing elit,consectetur adipiscing elitconsectetur adipiscing elitconsectetur adipiscing');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `ID` int UNSIGNED NOT NULL,
  `username` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `keyB` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `uuid` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`ID`, `username`, `keyB`, `uuid`) VALUES
(21, 'test12@gmail.com', 'Admin123!', '51ad9137-a36e-4b12-b462-bcd24b8b47cc'),
(22, 'test13@gmail.com', 'Test123!', '63efa610-be7f-481a-b194-1d90d03eec7a');

-- --------------------------------------------------------

--
-- Table structure for table `usersCompanies`
--

CREATE TABLE `usersCompanies` (
  `ID` int UNSIGNED NOT NULL,
  `userUUID` char(36) NOT NULL,
  `companyUUID` char(36) NOT NULL,
  `isAdmin` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `companies`
--
ALTER TABLE `companies`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `uuid` (`uuid`);

--
-- Indexes for table `passwords`
--
ALTER TABLE `passwords`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `userUUID` (`userUUID`),
  ADD KEY `uuid` (`uuid`);

--
-- Indexes for table `passwordsInfo`
--
ALTER TABLE `passwordsInfo`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `passID` (`passUUID`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `uuid` (`uuid`);

--
-- Indexes for table `usersCompanies`
--
ALTER TABLE `usersCompanies`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `companyUUID` (`companyUUID`),
  ADD KEY `userUUID` (`userUUID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `companies`
--
ALTER TABLE `companies`
  MODIFY `ID` int UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `passwords`
--
ALTER TABLE `passwords`
  MODIFY `ID` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `passwordsInfo`
--
ALTER TABLE `passwordsInfo`
  MODIFY `ID` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `ID` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `usersCompanies`
--
ALTER TABLE `usersCompanies`
  MODIFY `ID` int UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `passwords`
--
ALTER TABLE `passwords`
  ADD CONSTRAINT `passwords_ibfk_1` FOREIGN KEY (`userUUID`) REFERENCES `users` (`uuid`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `passwordsInfo`
--
ALTER TABLE `passwordsInfo`
  ADD CONSTRAINT `passwordsInfo_ibfk_1` FOREIGN KEY (`passUUID`) REFERENCES `passwords` (`uuid`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `usersCompanies`
--
ALTER TABLE `usersCompanies`
  ADD CONSTRAINT `usersCompanies_ibfk_1` FOREIGN KEY (`companyUUID`) REFERENCES `companies` (`uuid`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `usersCompanies_ibfk_2` FOREIGN KEY (`userUUID`) REFERENCES `users` (`uuid`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
