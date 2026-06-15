-- =====================================================
-- 医疗辅助系统数据库结构 (MySQL 版本)
-- 数据库: medical_assistant
-- =====================================================

-- 删除已存在的表（谨慎使用）
-- DROP TABLE IF EXISTS medical_records;
-- DROP TABLE IF EXISTS products;
-- DROP TABLE IF EXISTS users;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    age INT,
    city VARCHAR(50),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_city (city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 就诊记录表
CREATE TABLE IF NOT EXISTS medical_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    diagnosis TEXT,
    symptoms TEXT,
    treatment TEXT,
    prescription TEXT,
    visit_date DATE NOT NULL,
    doctor_name VARCHAR(50),
    department VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_visit_date (visit_date),
    INDEX idx_department (department)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 产品/药品表
CREATE TABLE IF NOT EXISTS products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2),
    category VARCHAR(50),
    stock INT DEFAULT 0,
    expiry_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入示例数据
INSERT IGNORE INTO users (name, email, age, city, phone) VALUES
    ('张三', 'zhangsan@example.com', 25, '北京', '13800000001'),
    ('李四', 'lisi@example.com', 30, '上海', '13800000002'),
    ('王五', 'wangwu@example.com', 35, '广州', '13800000003'),
    ('赵六', 'zhaoliu@example.com', 40, '深圳', '13800000004'),
    ('孙七', 'sunqi@example.com', 45, '杭州', '13800000005');

INSERT IGNORE INTO medical_records (user_id, diagnosis, symptoms, treatment, visit_date, doctor_name, department) VALUES
    (1, '感冒', '发烧、咳嗽、流鼻涕', '服用感冒药，多休息', '2026-05-15', '李医生', '内科'),
    (2, '高血压', '头晕、头痛', '服用降压药，低盐饮食', '2026-05-10', '王医生', '心血管科'),
    (3, '糖尿病', '多饮、多尿、体重下降', '胰岛素治疗，控制饮食', '2026-05-05', '张医生', '内分泌科');

INSERT IGNORE INTO products (name, price, category, stock, expiry_date) VALUES
    ('阿莫西林', 25.50, '抗生素', 100, '2027-12-31'),
    ('布洛芬', 18.00, '止痛药', 200, '2027-06-30'),
    ('二甲双胍', 35.00, '降糖药', 150, '2027-08-31'),
    ('硝苯地平', 28.50, '降压药', 80, '2027-10-31'),
    ('奥美拉唑', 42.00, '胃药', 120, '2027-09-30');