/*
 Navicat MySQL Data Transfer

 Source Server         : video
 Source Server Type    : MySQL
 Source Server Version : 50616
 Source Host           : rm-bp12bzgmvo85rflhio.mysql.rds.aliyuncs.com:3306
 Source Schema         : db_nt_video

 Target Server Type    : MySQL
 Target Server Version : 50616
 File Encoding         : 65001

 Date: 25/04/2019 11:11:16
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for video_token
-- ----------------------------
DROP TABLE IF EXISTS `video_token`;
CREATE TABLE `video_token` (
  `name` varchar(255) DEFAULT NULL,
  `token` varchar(255) DEFAULT NULL,
  `uid` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of video_token
-- ----------------------------
BEGIN;
INSERT INTO `video_token` VALUES ('小年糕', '7c357a432e43544fe974528fae5530ac', '0c4071b6-5d54-4665-bdd3-364b79d8a496');
INSERT INTO `video_token` VALUES ('小年糕祝福', '658561f5cad5ace806ed73db84af0179', '270bd624-46f5-483f-82ca-19aa07e1c374');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
