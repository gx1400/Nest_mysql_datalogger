## Nest_mysql_datalogger

This is project to log nest API data to a mySQL database.  The database table must be setup as follows:


CREATE DATABASE `nest` /*!40100 DEFAULT CHARACTER SET latin1 */;

CREATE TABLE `nest_log` (
  `index` int(11) NOT NULL auto_increment,
  `trans_time` bit(1) default NULL,
  `total_run_time` double default NULL,
  `leaf_temp` double default NULL,
  `target_type` varchar(45) default NULL,
  `total_run_time_away` double default NULL,
  `outside_temperature` double default NULL,
  `ac_state` varchar(45) default NULL,
  `time_stamp` timestamp NULL default NULL,
  `current_temperature` double default NULL,
  `away` bit(1) default NULL,
  `target_temp` double default NULL,
  `total_run_time_home` double default NULL,
  `fan_state` bit(1) default NULL,
  `total_trans_time` double default NULL,
  `humidity` double default NULL,
  `wind_dir` varchar(10) default NULL,
  `wind_mph` double default NULL,
  `weather_condition` varchar(45) default NULL,
  `heater_state` bit(1) default NULL,
  PRIMARY KEY  (`index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
