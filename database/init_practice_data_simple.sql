-- 初始化练习试卷相关数据
-- 注意：在执行此脚本前，请确保相关的表结构已经创建

-- 1. 创建练习试卷
INSERT INTO fater_practice_papers (title, description, type, difficulty, duration, totalScore, project_id, teacher_id, create_time, isActive) VALUES
('Java基础练习卷一', '包含Java基础知识的综合练习，适合初学者。', 'fixed', 'easy', 60, 100, 3, 'TEACHER001', '2024-12-20 10:00:00', 1),
('Python编程练习', 'Python编程基础概念和简单算法练习。', 'timed', 'medium', 45, 75, 2, 'TEACHER001', '2024-12-18 14:30:00', 1);

-- 2. 创建练习试卷题目关联
-- 使用现有的题目ID (假设题目1-10存在)
INSERT INTO fater_practice_paper_questions (paper_id, practise_id, questionOrder, score) VALUES
-- Java试卷题目
(1, 1, 1, 10), (1, 2, 2, 10), (1, 3, 3, 10), (1, 4, 4, 10), (1, 5, 5, 10),
(1, 9, 6, 10), (1, 10, 7, 10),
-- Python试卷题目
(2, 1, 1, 7.5), (2, 2, 2, 7.5), (2, 3, 3, 7.5), (2, 4, 4, 7.5), (2, 5, 5, 7.5),
(2, 9, 6, 7.5), (2, 10, 7, 7.5), (2, 11, 8, 7.5), (2, 12, 9, 7.5), (2, 13, 10, 7.5);

-- 3. 创建示例学生练习记录（用于测试）
INSERT INTO fater_student_practice_logs (student_id, paper_id, start_time, end_time, score, accuracy, usedTime, status) VALUES
('STUDENT001', 1, '2024-12-20 14:00:00', '2024-12-20 15:05:00', 85, 85, 65, 'completed');

-- 4. 创建示例答题记录（用于测试）
INSERT INTO fater_student_practice_answers (practice_log_id, practise_id, studentAnswer, answer_time, isCorrect, score) VALUES
(1, 1, 'A', '2024-12-20 14:05:00', 1, 10),
(1, 2, 'Java是一种编程语言', '2024-12-20 14:08:00', 1, 10),
(1, 3, 'B', '2024-12-20 14:12:00', 0, 0),
(1, 4, 'A', '2024-12-20 14:15:00', 1, 10),
(1, 5, 'a > b', '2024-12-20 14:18:00', 1, 10);
