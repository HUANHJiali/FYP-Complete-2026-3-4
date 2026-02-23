/*
SQLyog Community v13.2.0 (64 bit)
MySQL - 8.1.0 : Database - db_exam
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`db_exam` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `db_exam`;

/*Table structure for table `auth_group` */

DROP TABLE IF EXISTS `auth_group`;

CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `auth_group` */

/*Table structure for table `auth_group_permissions` */

DROP TABLE IF EXISTS `auth_group_permissions`;

CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `auth_group_permissions` */

/*Table structure for table `auth_permission` */

DROP TABLE IF EXISTS `auth_permission`;

CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `auth_permission` */

insert  into `auth_permission`(`id`,`name`,`content_type_id`,`codename`) values 
(1,'Can add log entry',1,'add_logentry'),
(2,'Can change log entry',1,'change_logentry'),
(3,'Can delete log entry',1,'delete_logentry'),
(4,'Can view log entry',1,'view_logentry'),
(5,'Can add permission',2,'add_permission'),
(6,'Can change permission',2,'change_permission'),
(7,'Can delete permission',2,'delete_permission'),
(8,'Can view permission',2,'view_permission'),
(9,'Can add group',3,'add_group'),
(10,'Can change group',3,'change_group'),
(11,'Can delete group',3,'delete_group'),
(12,'Can view group',3,'view_group'),
(13,'Can add user',4,'add_user'),
(14,'Can change user',4,'change_user'),
(15,'Can delete user',4,'delete_user'),
(16,'Can view user',4,'view_user'),
(17,'Can add content type',5,'add_contenttype'),
(18,'Can change content type',5,'change_contenttype'),
(19,'Can delete content type',5,'delete_contenttype'),
(20,'Can view content type',5,'view_contenttype'),
(21,'Can add session',6,'add_session'),
(22,'Can change session',6,'change_session'),
(23,'Can delete session',6,'delete_session'),
(24,'Can view session',6,'view_session'),
(25,'Can add colleges',7,'add_colleges'),
(26,'Can change colleges',7,'change_colleges'),
(27,'Can delete colleges',7,'delete_colleges'),
(28,'Can view colleges',7,'view_colleges'),
(29,'Can add grades',8,'add_grades'),
(30,'Can change grades',8,'change_grades'),
(31,'Can delete grades',8,'delete_grades'),
(32,'Can view grades',8,'view_grades'),
(33,'Can add projects',9,'add_projects'),
(34,'Can change projects',9,'change_projects'),
(35,'Can delete projects',9,'delete_projects'),
(36,'Can view projects',9,'view_projects'),
(37,'Can add users',10,'add_users'),
(38,'Can change users',10,'change_users'),
(39,'Can delete users',10,'delete_users'),
(40,'Can view users',10,'view_users'),
(41,'Can add teachers',11,'add_teachers'),
(42,'Can change teachers',11,'change_teachers'),
(43,'Can delete teachers',11,'delete_teachers'),
(44,'Can view teachers',11,'view_teachers'),
(45,'Can add students',12,'add_students'),
(46,'Can change students',12,'change_students'),
(47,'Can delete students',12,'delete_students'),
(48,'Can view students',12,'view_students'),
(49,'Can add practises',13,'add_practises'),
(50,'Can change practises',13,'change_practises'),
(51,'Can delete practises',13,'delete_practises'),
(52,'Can view practises',13,'view_practises'),
(53,'Can add options',14,'add_options'),
(54,'Can change options',14,'change_options'),
(55,'Can delete options',14,'delete_options'),
(56,'Can view options',14,'view_options'),
(57,'Can add exams',15,'add_exams'),
(58,'Can change exams',15,'change_exams'),
(59,'Can delete exams',15,'delete_exams'),
(60,'Can view exams',15,'view_exams'),
(61,'Can add exam logs',16,'add_examlogs'),
(62,'Can change exam logs',16,'change_examlogs'),
(63,'Can delete exam logs',16,'delete_examlogs'),
(64,'Can view exam logs',16,'view_examlogs'),
(65,'Can add answer logs',17,'add_answerlogs'),
(66,'Can change answer logs',17,'change_answerlogs'),
(67,'Can delete answer logs',17,'delete_answerlogs'),
(68,'Can view answer logs',17,'view_answerlogs');

/*Table structure for table `auth_user` */

DROP TABLE IF EXISTS `auth_user`;

CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `auth_user` */

/*Table structure for table `auth_user_groups` */

DROP TABLE IF EXISTS `auth_user_groups`;

CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `auth_user_groups` */

/*Table structure for table `auth_user_user_permissions` */

DROP TABLE IF EXISTS `auth_user_user_permissions`;

CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `auth_user_user_permissions` */

/*Table structure for table `django_admin_log` */

DROP TABLE IF EXISTS `django_admin_log`;

CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `django_admin_log` */

/*Table structure for table `django_content_type` */

DROP TABLE IF EXISTS `django_content_type`;

CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `django_content_type` */

insert  into `django_content_type`(`id`,`app_label`,`model`) values 
(1,'admin','logentry'),
(17,'app','answerlogs'),
(7,'app','colleges'),
(16,'app','examlogs'),
(15,'app','exams'),
(8,'app','grades'),
(14,'app','options'),
(13,'app','practises'),
(9,'app','projects'),
(12,'app','students'),
(11,'app','teachers'),
(10,'app','users'),
(3,'auth','group'),
(2,'auth','permission'),
(4,'auth','user'),
(5,'contenttypes','contenttype'),
(6,'sessions','session');

/*Table structure for table `django_migrations` */

DROP TABLE IF EXISTS `django_migrations`;

CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `django_migrations` */

insert  into `django_migrations`(`id`,`app`,`name`,`applied`) values 
(1,'contenttypes','0001_initial','2024-11-03 03:29:56.805354'),
(2,'auth','0001_initial','2024-11-03 03:29:57.345510'),
(3,'admin','0001_initial','2024-11-03 03:29:57.592878'),
(4,'admin','0002_logentry_remove_auto_add','2024-11-03 03:29:57.607838'),
(5,'admin','0003_logentry_add_action_flag_choices','2024-11-03 03:29:57.619829'),
(6,'app','0001_initial','2024-11-03 03:29:58.434349'),
(7,'contenttypes','0002_remove_content_type_name','2024-11-03 03:29:58.503165'),
(8,'auth','0002_alter_permission_name_max_length','2024-11-03 03:29:58.545052'),
(9,'auth','0003_alter_user_email_max_length','2024-11-03 03:29:58.566469'),
(10,'auth','0004_alter_user_username_opts','2024-11-03 03:29:58.574447'),
(11,'auth','0005_alter_user_last_login_null','2024-11-03 03:29:58.614341'),
(12,'auth','0006_require_contenttypes_0002','2024-11-03 03:29:58.619330'),
(13,'auth','0007_alter_validators_add_error_messages','2024-11-03 03:29:58.628304'),
(14,'auth','0008_alter_user_username_max_length','2024-11-03 03:29:58.669713'),
(15,'auth','0009_alter_user_last_name_max_length','2024-11-03 03:29:58.712598'),
(16,'auth','0010_alter_group_name_max_length','2024-11-03 03:29:58.732546'),
(17,'auth','0011_update_proxy_permissions','2024-11-03 03:29:58.752492'),
(18,'auth','0012_alter_user_first_name_max_length','2024-11-03 03:29:58.793549'),
(19,'sessions','0001_initial','2024-11-03 03:29:58.828456');

/*Table structure for table `django_session` */

DROP TABLE IF EXISTS `django_session`;

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `django_session` */

/*Table structure for table `fater_answer_logs` */

DROP TABLE IF EXISTS `fater_answer_logs`;

CREATE TABLE `fater_answer_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `score` double NOT NULL,
  `status` int NOT NULL,
  `answer` longtext NOT NULL,
  `no` int NOT NULL,
  `exam_id` int NOT NULL,
  `practises_id` int NOT NULL,
  `student_id` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fater_answer_logs_exam_id_273c58db_fk_fater_exams_id` (`exam_id`),
  KEY `fater_answer_logs_practises_id_026129f5_fk_fater_practises_id` (`practises_id`),
  KEY `fater_answer_logs_student_id_6f3e15e6_fk_fater_users_id` (`student_id`),
  CONSTRAINT `fater_answer_logs_exam_id_273c58db_fk_fater_exams_id` FOREIGN KEY (`exam_id`) REFERENCES `fater_exams` (`id`),
  CONSTRAINT `fater_answer_logs_practises_id_026129f5_fk_fater_practises_id` FOREIGN KEY (`practises_id`) REFERENCES `fater_practises` (`id`),
  CONSTRAINT `fater_answer_logs_student_id_6f3e15e6_fk_fater_users_id` FOREIGN KEY (`student_id`) REFERENCES `fater_users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `fater_answer_logs` */

insert  into `fater_answer_logs`(`id`,`score`,`status`,`answer`,`no`,`exam_id`,`practises_id`,`student_id`) values 
(1,0,0,'42',1,1,44,'S2019092300004'),
(2,0,0,'18',2,1,4,'S2019092300004'),
(3,0,0,'1',3,1,9,'S2019092300004'),
(4,0,0,'5',4,1,3,'S2019092300004'),
(5,0,0,'22',5,1,39,'S2019092300004'),
(6,0,0,'51',6,1,46,'S2019092300004'),
(7,0,0,'39',7,1,43,'S2019092300004'),
(8,0,0,'35',8,1,42,'S2019092300004'),
(9,0,0,'27',9,1,41,'S2019092300004'),
(10,0,0,'49',10,1,45,'S2019092300004'),
(11,0,0,'1',11,1,20,'S2019092300004'),
(12,0,0,'2',12,1,16,'S2019092300004'),
(13,0,0,'2',13,1,22,'S2019092300004'),
(14,0,0,'2',14,1,17,'S2019092300004'),
(15,0,0,'1',15,1,15,'S2019092300004'),
(16,0,0,'2',16,1,11,'S2019092300004'),
(17,0,0,'1',17,1,14,'S2019092300004'),
(18,0,0,'1',18,1,24,'S2019092300004'),
(19,0,0,'1',19,1,5,'S2019092300004'),
(20,0,0,'2',20,1,19,'S2019092300004'),
(21,0,0,'正确',21,1,27,'S2019092300004'),
(22,0,0,'正确',22,1,37,'S2019092300004'),
(23,0,0,'错误',23,1,29,'S2019092300004'),
(24,0,0,'正确',24,1,28,'S2019092300004'),
(25,0,0,'正确',25,1,38,'S2019092300004'),
(26,0,0,'正确',26,1,33,'S2019092300004'),
(27,0,0,'正确',27,1,35,'S2019092300004'),
(28,0,0,'正确',28,1,34,'S2019092300004'),
(29,0,0,'错误',29,1,32,'S2019092300004'),
(30,0,0,'错误',30,1,30,'S2019092300004'),
(31,0,0,'1',31,1,7,'S2019092300004'),
(32,0,0,'2',32,1,49,'S2019092300004');

/*Table structure for table `fater_colleges` */

DROP TABLE IF EXISTS `fater_colleges`;

CREATE TABLE `fater_colleges` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `create_time` varchar(19) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `fater_colleges` */

insert  into `fater_colleges`(`id`,`name`,`create_time`) values 
(1,'软件工程','2024-11-02 11:07:57'),
(2,'信息工程','2024-11-02 11:08:07');

/*Table structure for table `fater_exam_logs` */

DROP TABLE IF EXISTS `fater_exam_logs`;

CREATE TABLE `fater_exam_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `status` int NOT NULL,
  `score` double NOT NULL,
  `create_time` varchar(19) NOT NULL,
  `exam_id` int NOT NULL,
  `student_id` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fater_exam_logs_exam_id_e149415d_fk_fater_exams_id` (`exam_id`),
  KEY `fater_exam_logs_student_id_f32c21f4_fk_fater_users_id` (`student_id`),
  CONSTRAINT `fater_exam_logs_exam_id_e149415d_fk_fater_exams_id` FOREIGN KEY (`exam_id`) REFERENCES `fater_exams` (`id`),
  CONSTRAINT `fater_exam_logs_student_id_f32c21f4_fk_fater_users_id` FOREIGN KEY (`student_id`) REFERENCES `fater_users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `fater_exam_logs` */

insert  into `fater_exam_logs`(`id`,`status`,`score`,`create_time`,`exam_id`,`student_id`) values 
(1,1,0,'2024-11-03 11:48:20',1,'S2019092300004');

/*Table structure for table `fater_exams` */

DROP TABLE IF EXISTS `fater_exams`;

CREATE TABLE `fater_exams` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `create_time` varchar(19) NOT NULL,
  `exam_time` varchar(19) NOT NULL,
  `grade_id` int NOT NULL,
  `project_id` int NOT NULL,
  `teacher_id` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fater_exams_grade_id_851edd59_fk_fater_grades_id` (`grade_id`),
  KEY `fater_exams_project_id_08b945f8_fk_fater_projects_id` (`project_id`),
  KEY `fater_exams_teacher_id_2e131d20_fk_fater_users_id` (`teacher_id`),
  CONSTRAINT `fater_exams_grade_id_851edd59_fk_fater_grades_id` FOREIGN KEY (`grade_id`) REFERENCES `fater_grades` (`id`),
  CONSTRAINT `fater_exams_project_id_08b945f8_fk_fater_projects_id` FOREIGN KEY (`project_id`) REFERENCES `fater_projects` (`id`),
  CONSTRAINT `fater_exams_teacher_id_2e131d20_fk_fater_users_id` FOREIGN KEY (`teacher_id`) REFERENCES `fater_users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `fater_exams` */

insert  into `fater_exams`(`id`,`name`,`create_time`,`exam_time`,`grade_id`,`project_id`,`teacher_id`) values 
(1,'sfs','2024-11-03 11:45:32','2024-11-03 11:48:00',1,3,'T2010012000001');

/*Table structure for table `fater_grades` */

DROP TABLE IF EXISTS `fater_grades`;

CREATE TABLE `fater_grades` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `create_time` varchar(19) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `fater_grades` */

insert  into `fater_grades`(`id`,`name`,`create_time`) values 
(1,'一年级一班','2024-11-02 11:08:22'),
(2,'一年级二班','2024-11-02 11:08:31'),
(3,'二年级一班','2024-11-02 11:08:42'),
(4,'二年级二班','2024-11-02 11:08:48'),
(5,'三年级一班','2024-11-02 11:08:57'),
(6,'三年级二班','2024-11-02 11:09:02');

/*Table structure for table `fater_options` */

DROP TABLE IF EXISTS `fater_options`;

CREATE TABLE `fater_options` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `practise_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fater_options_practise_id_31fd821f_fk_fater_practises_id` (`practise_id`),
  CONSTRAINT `fater_options_practise_id_31fd821f_fk_fater_practises_id` FOREIGN KEY (`practise_id`) REFERENCES `fater_practises` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `fater_options` */

insert  into `fater_options`(`id`,`name`,`practise_id`) values 
(1,'int',9),
(2,'double',9),
(3,'String',9),
(4,'boolean',9),
(5,'java',3),
(6,'class',3),
(7,'exe',3),
(8,'txt',3),
(9,'txt',2),
(10,'exe',2),
(11,'java',2),
(12,'class',2),
(13,'number',1),
(14,'int',1),
(15,'float',1),
(16,'double',1),
(17,'Eclipse',4),
(18,'IDEA',4),
(19,'JDK',4),
(20,'JRE',4),
(21,'public',39),
(22,'private',39),
(23,'protected',39),
(24,'final',39),
(25,'char c = \" \"',41),
(26,'char c = \'A\'',41),
(27,'char c = \'男\'',41),
(33,'char c = \' \'',41),
(34,'int num;',42),
(35,'int num = 23;',42),
(36,'double num = 23.0;',42),
(37,'float num = 23.0;',42),
(38,'static',43),
(39,'goto',43),
(40,'while',43),
(41,'then',43),
(42,'父类中被 final 修饰的方法',44),
(43,'父类中被 private 修饰的方法',44),
(44,'父类中被 abstract 修饰的方法',44),
(45,'任何情况下都可以',44),
(46,'JDK',45),
(47,'JVM',45),
(48,'IDEA',45),
(49,'Eclipse',45),
(50,'Java SE',46),
(51,'Java EE',46),
(52,'Java ME',46),
(53,'Java HE',46),
(54,'Java的main方法必须写在类里',47),
(55,'Java程序中可以包括多个main方法',47),
(56,'Java程序类名必须和文件名保持一致',47),
(57,'main方法只有一行代码时可以省略{}',47),
(58,'类定义时',48),
(59,'创建对象时',48),
(60,'调用对象方法时',48),
(61,'使用对象的变量时',48),
(62,'元祖',50),
(63,'列表',50),
(64,'字典',50),
(65,'指针',50);

/*Table structure for table `fater_practises` */

DROP TABLE IF EXISTS `fater_practises`;

CREATE TABLE `fater_practises` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `answer` longtext NOT NULL,
  `analyse` longtext NOT NULL,
  `type` int NOT NULL,
  `create_time` varchar(19) NOT NULL,
  `project_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fater_practises_project_id_fbd7cb5b_fk_fater_projects_id` (`project_id`),
  CONSTRAINT `fater_practises_project_id_fbd7cb5b_fk_fater_projects_id` FOREIGN KEY (`project_id`) REFERENCES `fater_projects` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `fater_practises` */

insert  into `fater_practises`(`id`,`name`,`answer`,`analyse`,`type`,`create_time`,`project_id`) values 
(1,'JAVA数据类型不包括哪些','13','无',0,'2024-11-03 15:45:34',3),
(2,'Java源代码文件的后缀名是','11','无',0,'2024-11-03 15:47:56',3),
(3,'Java编译后文件的后缀名是','6','无',0,'2024-11-03 15:48:08',3),
(4,'运行Java程序必须安装','20','无',0,'2024-11-03 15:48:32',3),
(5,'面向对象的特征包括封装、继承、____','多态','无',1,'2024-11-03 15:49:57',3),
(6,'Java基本数据类型不包括 Boolean','正确','boolean 是基础类型，Boolean 是它包装类型，属于引用类型',2,'2024-11-03 15:51:56',3),
(7,'输入整数a、b，编程实现两个数字值互换','public static void main(String[] args) {\n	\n	Scanner input = new Scanner(System.in);\n	\n	System.out.println(\"请输入数字 a: \");\n	int a = input.nextInt();\n	\n\n	System.out.println(\"请输入数字 b: \");\n	int b = input.nextInt();\n	\n	int c = a;\n	a = b;\n	b = c;\n	\n	System.out.println(\"交换后，a 的值是：\" + a + \", b 的值是：\" + b);\n}','无',3,'2024-11-03 15:56:06',3),
(8,'输入整数a、b，编程判断两个数字大小','public static void main(String[] args) {\n	\n	Scanner input = new Scanner(System.in);\n	\n	System.out.println(\"请输入数字 a: \");\n	int a = input.nextInt();\n	\n\n	System.out.println(\"请输入数字 b: \");\n	int b = input.nextInt();\n\n	\n	if(a > b) {\n		\n		System.out.println(\"数字 a 大于数字 b\");\n	}else {\n		\n		System.out.println(\"数字 a 小于数字 b\");\n	}\n}','无',3,'2024-11-03 15:59:21',3),
(9,'Java基本数据类型不包括','3','无',0,'2024-11-03 16:01:11',3),
(10,'Java支持跨平台开发','正确','无',2,'2024-11-03 16:05:44',3),
(11,'Java数据类型之间的转换包括自动化转换和____','强制转换','无',1,'2024-11-03 16:11:16',3),
(12,'Java程序运行需要经过编写、___ 和 运行','编译','无',1,'2024-11-04 09:34:21',3),
(13,'Java中布尔类型的值包括 ___ 和 false','true','无',1,'2024-11-04 09:35:29',3),
(14,'Java程序中进行逻辑判断可以使用 if、___ 结构','switch','无',1,'2024-11-04 09:39:26',3),
(15,'Java程序中结束循环可以使用break、___','continue','无',1,'2024-11-04 09:41:17',3),
(16,'构造方法在 ___ 时候调用','创建对象','无',1,'2024-11-04 09:42:04',3),
(17,'___ 作为修饰符修饰变量其他类中无法访问','private','无',1,'2024-11-04 09:44:39',3),
(18,'___ 表示方法没有返回值','void','无',1,'2024-11-04 09:45:29',3),
(19,'___ 是定义类必须使用的关键字','class','无',1,'2024-11-04 09:47:46',3),
(20,'___ 方法仅有定义没有具体实现','抽象','无',1,'2024-11-04 09:49:08',3),
(21,'___ 修饰的方法不能被子类重写','final','无',1,'2024-11-04 09:50:09',3),
(22,'JDK安装之后，开发工具在 ___ 文件夹中','bin','无',1,'2024-11-04 09:51:23',3),
(23,'__ 指令是编译Java源代码时使用的','javac','无',1,'2024-11-04 09:52:27',3),
(24,'__ 指令是运行Java程序时使用的','java','无',1,'2024-11-04 09:52:52',3),
(25,'一个完整的Java程序必须包含一个主程序，其中必定包含一个 ___ 方法','main','无',1,'2024-11-04 09:54:15',3),
(26,'JAVA是编译解释型的编程语言','正确','无',2,'2024-11-04 09:55:12',3),
(27,'运行Java程序必须先编译后运行','正确','无',2,'2024-11-04 09:55:52',3),
(28,'Java中布尔类型值包括 True','错误','无',2,'2024-11-04 09:56:38',3),
(29,'Java不同数据类型长度是固定的，不会随机器硬件发生改变','正确','无',2,'2024-11-04 09:58:57',3),
(30,'Java程序中switch结构只能用来做等值判断','正确','无',2,'2024-11-04 10:00:08',3),
(31,'Java程序中未经初始化的变量可以直接使用','错误','无',2,'2024-11-04 10:01:10',3),
(32,'abstract 可以用来修饰抽象方法','正确','无',2,'2024-11-04 10:03:00',3),
(33,'final 修饰的方法无法在子类中被重写','正确','无',2,'2024-11-04 10:03:30',3),
(34,'static 修饰的方法可以使用对象调用','正确','无',2,'2024-11-04 10:03:59',3),
(35,'static 不能用来修饰类','正确','无',2,'2024-11-04 10:06:36',3),
(36,'子类会继承父类所有的非私有属性和方法','正确','无',2,'2024-11-04 10:07:49',3),
(37,'抽象方法可以不包括实现代码','错误','无',2,'2024-11-04 10:12:19',3),
(38,'多态是面向对象的三大特征之一','正确','无',2,'2024-11-04 10:15:59',3),
(39,'访问修饰符不包括','24','无',0,'2024-11-04 10:17:29',3),
(41,'char 类型使用不正确的是','25','无',0,'2024-11-04 15:15:24',3),
(42,'下列声明方式不正确的是','37','float 类型声明需要在数值后边加 f ',0,'2024-11-04 15:38:32',3),
(43,'下列不属于 Java 语言关键字的是','41','无',0,'2024-11-04 15:41:54',3),
(44,'什么情况下子类继承的方法不能重写','42','final 表示最终的',0,'2024-11-04 15:48:56',3),
(45,'编写Java代码我们必须安装什么','46','无',0,'2024-11-04 15:53:12',3),
(46,'Java版本不包括','53','无',0,'2024-11-04 15:55:48',3),
(47,'下列说法正确的是','54','无',0,'2024-11-04 15:57:24',3),
(48,'构造函数何时被调用','59','无',0,'2024-11-04 16:00:15',3),
(49,'输入a、b、c，输出其中最大的数','public static void main(String[] args) {\n	\n	Scanner input = new Scanner(System.in);\n	\n	System.out.println(\"请输入数字 a: \");\n	int a = input.nextInt();\n	\n\n	System.out.println(\"请输入数字 b: \");\n	int b = input.nextInt();\n\n	System.out.println(\"请输入数字 c: \");\n	int c = input.nextInt();\n	\n	if(a > b) {\n		\n		if(a > c) {\n			\n			System.out.println(\"最大的数是: \" + a);\n		}else {\n			\n			System.out.println(\"最大的数是: \" + c);\n		}\n	}else {\n		\n		if(b > c) {\n			\n			System.out.println(\"最大的数是: \" + b);\n		}else {\n			\n			System.out.println(\"最大的数是: \" + c);\n		}\n	}\n}','无',3,'2024-11-04 16:02:41',3),
(50,'python的数据类型不包括','65','无',0,'2024-11-11 15:34:10',2),
(51,'Python中 ___ 表示空类型','None','无',1,'2024-11-11 15:36:58',2),
(52,'python代码文件的后缀名是 python','错误','无',2,'2024-11-11 15:38:36',2);

/*Table structure for table `fater_projects` */

DROP TABLE IF EXISTS `fater_projects`;

CREATE TABLE `fater_projects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `create_time` varchar(19) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `fater_projects` */

insert  into `fater_projects`(`id`,`name`,`create_time`) values 
(1,'C语言','2024-11-02 11:18:03'),
(2,'Python','2024-11-02 11:18:12'),
(3,'Java','2024-11-02 11:18:21'),
(4,'软件测试','2024-11-02 11:18:38');

/*Table structure for table `fater_students` */

DROP TABLE IF EXISTS `fater_students`;

CREATE TABLE `fater_students` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `college_id` int NOT NULL,
  `grade_id` int NOT NULL,
  `user_id` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `fater_students_college_id_6442f849_fk_fater_colleges_id` (`college_id`),
  KEY `fater_students_grade_id_11f9bb1a_fk_fater_grades_id` (`grade_id`),
  CONSTRAINT `fater_students_college_id_6442f849_fk_fater_colleges_id` FOREIGN KEY (`college_id`) REFERENCES `fater_colleges` (`id`),
  CONSTRAINT `fater_students_grade_id_11f9bb1a_fk_fater_grades_id` FOREIGN KEY (`grade_id`) REFERENCES `fater_grades` (`id`),
  CONSTRAINT `fater_students_user_id_3752efbf_fk_fater_users_id` FOREIGN KEY (`user_id`) REFERENCES `fater_users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `fater_students` */

insert  into `fater_students`(`id`,`college_id`,`grade_id`,`user_id`) values 
(2,1,3,'S2019092300001'),
(3,1,3,'S2019092300002'),
(4,1,4,'S2019092300003'),
(5,1,1,'S2019092300004');

/*Table structure for table `fater_teachers` */

DROP TABLE IF EXISTS `fater_teachers`;

CREATE TABLE `fater_teachers` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `phone` varchar(11) NOT NULL,
  `record` varchar(10) NOT NULL,
  `job` varchar(20) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `fater_teachers_user_id_5dade1e2_fk_fater_users_id` FOREIGN KEY (`user_id`) REFERENCES `fater_users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `fater_teachers` */

insert  into `fater_teachers`(`id`,`phone`,`record`,`job`,`user_id`) values 
(3,'30920390','本科','助理讲师','T2010012000001'),
(4,'30920391','研究生','普通教员','T2010012000002');

/*Table structure for table `fater_users` */

DROP TABLE IF EXISTS `fater_users`;

CREATE TABLE `fater_users` (
  `id` varchar(20) NOT NULL,
  `user_name` varchar(32) NOT NULL,
  `pass_word` varchar(32) NOT NULL,
  `name` varchar(20) NOT NULL,
  `gender` varchar(4) NOT NULL,
  `age` int NOT NULL,
  `type` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `fater_users` */

insert  into `fater_users`(`id`,`user_name`,`pass_word`,`name`,`gender`,`age`,`type`) values 
('1','python222','123456','张三丰','男',45,0),
('S2019092300001','zhangwuji','zhangwuji','张无忌','男',23,2),
('S2019092300002','songqingshu','songqingshu','宋青书','男',23,2),
('S2019092300003','zhouzhiruo','zhouzhiruo','周芷若','女',23,2),
('S2019092300004','zhujiuzhen','zhujiuzhen','朱九真','女',19,2),
('T2010012000001','zhuchanglin','zhuchanglin','朱长龄','男',35,1),
('T2010012000002','songyuanqiao','songyuanqiao','宋远桥','男',42,1);

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
