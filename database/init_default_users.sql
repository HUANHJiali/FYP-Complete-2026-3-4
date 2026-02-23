-- 初始化默认用户账户
-- 根据 DOCKER_DEPLOYMENT.md 中的默认账户配置创建
-- 注意：如果用户已存在，使用 INSERT IGNORE 或先检查再插入

-- 删除已存在的默认账户（如果存在）
DELETE FROM `fater_users` WHERE `user_name` IN ('admin', 'teacher', 'student');

-- 插入默认账户
-- 管理员账户 (type=0)
INSERT INTO `fater_users` (`id`, `user_name`, `pass_word`, `name`, `gender`, `age`, `type`) 
VALUES ('ADMIN001', 'admin', '123456', '系统管理员', '男', 30, 0);

-- 教师账户 (type=1)
INSERT INTO `fater_users` (`id`, `user_name`, `pass_word`, `name`, `gender`, `age`, `type`) 
VALUES ('TEACHER001', 'teacher', '123456', '教师账户', '男', 35, 1);

-- 学生账户 (type=2)
INSERT INTO `fater_users` (`id`, `user_name`, `pass_word`, `name`, `gender`, `age`, `type`) 
VALUES ('STUDENT001', 'student', '123456', '学生账户', '男', 20, 2);

-- 创建教师关联信息
DELETE FROM `fater_teachers` WHERE `user_id` = 'TEACHER001';
INSERT INTO `fater_teachers` (`user_id`, `phone`, `record`, `job`) 
VALUES ('TEACHER001', '13800000000', '本科', '讲师');

-- 创建学生关联信息（需要确保college_id和grade_id存在）
DELETE FROM `fater_students` WHERE `user_id` = 'STUDENT001';
-- 使用默认的college_id=1和grade_id=1，如果不存在请先创建
INSERT INTO `fater_students` (`user_id`, `college_id`, `grade_id`) 
VALUES ('STUDENT001', 1, 1);

-- 验证插入结果
SELECT `id`, `user_name`, `name`, `type`, 
       CASE `type` 
         WHEN 0 THEN '管理员'
         WHEN 1 THEN '教师'
         WHEN 2 THEN '学生'
         ELSE '未知'
       END AS `role`
FROM `fater_users` 
WHERE `user_name` IN ('admin', 'teacher', 'student')
ORDER BY `type`;

