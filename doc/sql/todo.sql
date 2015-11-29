/*
MySQL Data Transfer
Source Host: localhost
Source Database: todo
Target Host: localhost
Target Database: todo
Date: 2011/6/25 21:57:10
*/

SET FOREIGN_KEY_CHECKS=0;
-- ----------------------------
-- Table structure for pd_user
-- ----------------------------
DROP TABLE IF EXISTS `pd_user`;
CREATE TABLE `pd_user` (
  `u_id` int NOT NULL AUTO_INCREMENT ,
  `u_from` VARCHAR(10) NULL DEFAULT 0 COMMENT '1. sina\n2. qq\n0. local' ,
  `u_auth` CHAR(100) NULL COMMENT '第三方的唯一标识\n' ,
  `u_name` CHAR(100) NOT NULL COMMENT '昵称' ,
  `u_birthday` VARCHAR(45) NULL COMMENT '出生日期' ,
  `u_sex` SMALLint NULL DEFAULT 1 COMMENT '1.male\n2.female' ,
  `u_create_time` int NOT NULL DEFAULT 0 COMMENT '用户注册时间' ,
  `u_logo` CHAR(100) NULL ,
  `u_email` VARCHAR(100) NOT NULL COMMENT '用户邮箱:\n用于收通知邮件\n' ,
  `u_pass` VARCHAR(100) NULL COMMENT '密码' ,
  `u_description` VARCHAR(200) NULL ,
  PRIMARY KEY (`u_id`) ,
  UNIQUE INDEX `index_email` (`u_email` ASC) ,
  UNIQUE INDEX `index_name` (`u_name` ASC) )
ENGINE = InnoDB
AUTO_INCREMENT = 100000
DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for pd_todo
-- ----------------------------
DROP TABLE IF EXISTS `pd_todo`;
CREATE TABLE `pd_todo` (
  `t_id` int(11) NOT NULL auto_increment,
  `t_title` varchar(300) default NULL COMMENT '任务内容',
  `t_share` int default 1 COMMENT '是否共享',
  `t_create_uid` int NOT NULL COMMENT '任务创建人',  
  `t_commond` varchar(300) default NULL COMMENT '任务指令' ,
  `t_create_date` datetime default NULL COMMENT '任务创建时间' ,
  `t_finished` int(11) default '0' COMMENT '任务状态 0.未完成 1.完成' ,
  `t_finished_uid` int NOT NULL COMMENT '任务完成人',
  `t_finished_date` datetime default NULL COMMENT '任务完成时间',
  PRIMARY KEY  (`t_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for pd_find_pass
-- ----------------------------
DROP TABLE IF EXISTS `pd_find_pass`;
CREATE TABLE `pd_find_pass` (
  `f_uemail` VARCHAR(30) NOT NULL ,
  `f_hash` CHAR(64) NOT NULL ,
  `f_create_time` int NULL ,
  PRIMARY KEY (`f_uemail`, `f_hash`) )
ENGINE = InnoDB DEFAULT CHARSET=utf8 COMMENT = '用于找回密码';
