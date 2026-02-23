-- =====================================================
-- 安全修复：修改Users表密码字段长度
-- 问题：当前密码字段最大长度仅32字符，无���正确存储Django加密后的密码（需要60+字符）
-- 风险：高危 - 可能导致加密密码被截断，造成安全隐患
-- =====================================================

-- 修改密码字段长度从32到128字符
ALTER TABLE fater_users MODIFY COLUMN pass_word VARCHAR(128) NOT NULL;

-- 验证修改结果
SELECT
    COLUMN_NAME,
    COLUMN_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE
FROM
    INFORMATION_SCHEMA.COLUMNS
WHERE
    TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'fater_users'
    AND COLUMN_NAME = 'pass_word';

-- 说明：
-- 1. Django的make_password()生成的加密密码格式为：
--    <algorithm>$<iterations>$<salt>$<hash>
--    例如：pbkdf2_sha256$150000$JJ5F7uXJ5dGY$K3mU9s8r9n0mK9j8h7g6f5d4s3a2z1x0c9v8b7n6m5
--    通常需要60+字符，设置128字符可以确保有足够空间
--
-- 2. 修改后需要重启Django应用以更新模型
--
-- 3. 已有的明文密码不受影响，加密密码也不会被截断
--
-- 4. 建议在非高峰期执行此修改
