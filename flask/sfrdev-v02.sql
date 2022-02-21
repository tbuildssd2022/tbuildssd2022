-- MySQL Script generated by MySQL Workbench
-- Mon Feb 21 14:13:23 2022
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema sfrdev
-- -----------------------------------------------------
-- Development instance  secure file repository
-- 
-- Combining access control and storage in same database to simplify replication
-- 
-- 
DROP SCHEMA IF EXISTS `sfrdev` ;

-- -----------------------------------------------------
-- Schema sfrdev
--
-- Development instance  secure file repository
-- 
-- Combining access control and storage in same database to simplify replication
-- 
-- 
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `sfrdev` DEFAULT CHARACTER SET utf8 ;
USE `sfrdev` ;

-- -----------------------------------------------------
-- Table `sfrdev`.`datauser`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `sfrdev`.`datauser` ;

CREATE TABLE IF NOT EXISTS `sfrdev`.`datauser` (
  `userid` INT NOT NULL AUTO_INCREMENT COMMENT 'auto incrementing digits,  obscured from user because they pass accessid on login page.',
  `userforename` VARCHAR(45) NOT NULL,
  `usersurname` VARCHAR(45) NOT NULL,
  `userdisplayname` VARCHAR(90) NOT NULL COMMENT 'Minimum 1 character,  max 90',
  `useraccessid` VARCHAR(12) NOT NULL COMMENT ' character agency / company code followed by up to 5 digits and 1 random letters   abcd87e497   ~ 250,000 possible usernames  Unique constraint should handle any name space collisions)',
  `useragency` VARCHAR(45) NULL COMMENT 'Name of space agency user is associated with.  User can only belong to on space agency. Potential for normalization in the future releases, agency management was out of scope',
  `authgroups` VARCHAR(60) NULL COMMENT 'Can contain zero to 20 2 digit numbers that represent groups the user could belong to. This provides a possible 99 unique groups.  Seperate each group identifier with a comma simplify the function retrieving membership. ',
  PRIMARY KEY (`userid`),
  UNIQUE INDEX `useraccessid_UNIQUE` (`useraccessid` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `sfrdev`.`userauthnz`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `sfrdev`.`userauthnz` ;

CREATE TABLE IF NOT EXISTS `sfrdev`.`userauthnz` (
  `userid` INT NOT NULL COMMENT 'Each new user account created will have a unique ID but this is a foreign key from the auto-incremented data user table. Therefore reuse of account names, access ID\'s etc will always reflect the most current user.  Auto-increment also ensures no account ID could accidently be reused (authorization for file access is based on group membership but file ownership is tied to userid) ',
  `userpasswd` VARCHAR(102) NOT NULL COMMENT 'Using WerkZeug security built in function for generating for storing ',
  `userlocked` TINYINT NOT NULL DEFAULT 0 COMMENT 'Boolean value that can be set is suspicous activity is detected for a given account, allows quick protection and subsequent unlocking without forcing a password change\n',
  `forcepwdchange` TINYINT NOT NULL DEFAULT 0 COMMENT 'Place holder for future implementation phase\n',
  `activestatus` TINYINT NOT NULL DEFAULT 1 COMMENT 'User information may need to be retained for the puposes of maintaining file ownership ortransaction history. Inactive accounts provide a possible application compromise path, checking enabled/disabled can be implemented programatically even before testing passwords, reducing the feasibilty of attacks like password spraying or credential stuffing\n',
  `passwdchange` DATETIME NULL COMMENT 'Placeholder for future enhancement to enforce periodic password rotation',
  `userregistration` DATETIME NOT NULL COMMENT 'Date user account was created, forcing as a required field to support non-repudiation and security incident investigation requirements',
  PRIMARY KEY (`userid`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `sfrdev`.`datagroups`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `sfrdev`.`datagroups` ;

CREATE TABLE IF NOT EXISTS `sfrdev`.`datagroups` (
  `groupid` INT NOT NULL COMMENT 'two digit group number 00 - 99 gives 100 possible groups\n',
  `groupname` VARCHAR(45) NOT NULL COMMENT 'Human readable name, use underscores instead of spaces.  Naming convention TBD',
  `groupdesc` VARCHAR(90) NULL COMMENT 'Human readable description of group function and data classification',
  `grouptype` INT NOT NULL COMMENT 'Encode group function using integer values,  EG 1 = open research,  2 = commercial research, 3 = agency proprietary  etc.',
  PRIMARY KEY (`groupid`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `sfrdev`.`storedfiles`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `sfrdev`.`storedfiles` ;

CREATE TABLE IF NOT EXISTS `sfrdev`.`storedfiles` (
  `uuid_hex` VARCHAR(32) NOT NULL,
  `filename` VARCHAR(128) NOT NULL COMMENT 'Maximum file name size if 128 characters including extention and dot seperator',
  `filetype` VARCHAR(8) NOT NULL COMMENT 'This should normally be 3 or 4,  things .tar.gz may be observed but we should actually reject anything with more than one extension as suspicious  8 seems like all we\'d every need at this point ',
  `filedata` LONGBLOB NOT NULL COMMENT 'Long blob provides up to 4 gigabyte of storage but this app also processes only in memory so we need to cap the files at 32 or 64 meg for now.  both exeed the next largest blob size, 16 meg.  If performance were really an issue this could be dropped to a medium blob if 16 meg is an acceptable limit.  This seems less likely in a science data situation, large files are not uncommon.',
  `fileowner` INT NOT NULL COMMENT 'File owner value is int,  this will suppport thousands of users over time, can be assured to be unique with the database.  ',
  `authgroups` VARCHAR(60) NULL COMMENT 'Allows up to 20 groups to be granted access to a specific file. This can be null since the owner can always be granted access to their files but they may not share them with anyone.\nData content will be 2 digit numbers, comma seperated, no spaces.  This can be brought in from the object to the authorization code as a list.  ',
  `filecreate` DATETIME NOT NULL COMMENT 'This will be automatically generated on upload and used for inital insert. This becomes a non-repudiation control when combined with the owner ID which is also automatically retrieved from the logged in user. \n( New versions of the file will have a new date, which can be used to track versions.) The core issue with this is duplicate file names but if we include file size and date they could tell them apart.  ',
  `filesize` INT NOT NULL COMMENT 'Store this as a value in the class so we can request this as part of getfilemetadata() instead of calculating it off the raw bytes.  This will be useful for presenting since it will be a consistent response time.',
  `keywords_tags` VARCHAR(255) NULL COMMENT 'Use 255 for max keywords & tags.  Can be null.  ',
  PRIMARY KEY (`uuid_hex`))
ENGINE = InnoDB;

SET SQL_MODE = '';
DROP USER IF EXISTS sfr_app;
SET SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
CREATE USER 'sfr_app' IDENTIFIED BY 'n0t2S#CR#T!';

GRANT ALL ON `sfrdev`.* TO 'sfr_app';

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
