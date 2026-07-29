-- =============================================================================
-- Vehicle Damage Insurance ERP — Complete MySQL Database Schema Script
-- Target Database: Vehicle_Analyzis
-- Character Set: utf8mb4 | Collation: utf8mb4_unicode_ci
-- Compatible with phpMyAdmin and MySQL 8.x / MariaDB
-- =============================================================================

CREATE DATABASE IF NOT EXISTS `Vehicle_Analyzis`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE `Vehicle_Analyzis`;

-- -----------------------------------------------------------------------------
-- Table 1: roles
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `roles` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `code` VARCHAR(30) NOT NULL,
  `name` VARCHAR(60) NOT NULL,
  `description` VARCHAR(255) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_roles_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 2: customers
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `customers` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `customer_code` VARCHAR(30) NOT NULL,
  `full_name` VARCHAR(150) NOT NULL,
  `nic_or_passport` VARCHAR(60) NULL,
  `date_of_birth` DATE NULL,
  `phone_primary` VARCHAR(30) NOT NULL,
  `phone_secondary` VARCHAR(30) NULL,
  `email` VARCHAR(255) NOT NULL,
  `address_line_1` VARCHAR(255) NOT NULL,
  `address_line_2` VARCHAR(255) NULL,
  `city` VARCHAR(100) NOT NULL,
  `postal_code` VARCHAR(20) NULL,
  `notes` TEXT NULL,
  `status` VARCHAR(20) NOT NULL DEFAULT 'active',
  `created_by` BIGINT UNSIGNED NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_customers_code` (`customer_code`),
  UNIQUE KEY `uk_customers_nic` (`nic_or_passport`),
  KEY `idx_customers_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 3: users
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `role_id` BIGINT UNSIGNED NOT NULL,
  `customer_id` BIGINT UNSIGNED NULL,
  `username` VARCHAR(80) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `must_change_password` TINYINT(1) NOT NULL DEFAULT 1,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `failed_login_count` INT NOT NULL DEFAULT 0,
  `locked_until` DATETIME NULL,
  `last_login_at` DATETIME NULL,
  `password_changed_at` DATETIME NULL,
  `created_by` BIGINT UNSIGNED NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_users_username` (`username`),
  UNIQUE KEY `uk_users_email` (`email`),
  KEY `idx_users_role` (`role_id`),
  KEY `idx_users_customer` (`customer_id`),
  KEY `idx_users_active` (`is_active`),
  CONSTRAINT `fk_users_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `fk_users_customer` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Update customers table foreign key to users
ALTER TABLE `customers` ADD CONSTRAINT `fk_customers_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL;

-- -----------------------------------------------------------------------------
-- Table 4: vehicles
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `vehicles` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `customer_id` BIGINT UNSIGNED NOT NULL,
  `vehicle_code` VARCHAR(30) NOT NULL,
  `registration_number` VARCHAR(40) NOT NULL,
  `chassis_number` VARCHAR(80) NULL,
  `engine_number` VARCHAR(80) NULL,
  `make` VARCHAR(100) NOT NULL,
  `model` VARCHAR(100) NOT NULL,
  `manufactured_year` SMALLINT NULL,
  `colour` VARCHAR(60) NOT NULL,
  `vehicle_type` VARCHAR(40) NOT NULL DEFAULT 'Car',
  `fuel_type` VARCHAR(40) NULL,
  `odometer_km` INT NULL,
  `primary_image_id` BIGINT UNSIGNED NULL,
  `status` VARCHAR(20) NOT NULL DEFAULT 'active',
  `created_by` BIGINT UNSIGNED NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_vehicles_code` (`vehicle_code`),
  UNIQUE KEY `uk_vehicles_reg` (`registration_number`),
  UNIQUE KEY `uk_vehicles_chassis` (`chassis_number`),
  KEY `idx_vehicles_customer` (`customer_id`),
  CONSTRAINT `fk_vehicles_customer` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 5: insurance_plans
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `insurance_plans` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `plan_code` VARCHAR(30) NOT NULL,
  `name` VARCHAR(120) NOT NULL,
  `description` TEXT NOT NULL,
  `coverage_limit` DECIMAL(15,2) NULL,
  `deductible_amount` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
  `currency_code` CHAR(3) NOT NULL DEFAULT 'LKR',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_by` BIGINT UNSIGNED NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_plans_code` (`plan_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 6: vehicle_policies
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `vehicle_policies` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `vehicle_id` BIGINT UNSIGNED NOT NULL,
  `plan_id` BIGINT UNSIGNED NOT NULL,
  `policy_number` VARCHAR(80) NOT NULL,
  `start_date` DATE NOT NULL,
  `end_date` DATE NOT NULL,
  `premium_amount` DECIMAL(15,2) NULL,
  `status` VARCHAR(20) NOT NULL DEFAULT 'active',
  `notes` TEXT NULL,
  `created_by` BIGINT UNSIGNED NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_policies_num` (`policy_number`),
  KEY `idx_policies_vehicle` (`vehicle_id`),
  KEY `idx_policies_plan` (`plan_id`),
  CONSTRAINT `fk_policies_vehicle` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`),
  CONSTRAINT `fk_policies_plan` FOREIGN KEY (`plan_id`) REFERENCES `insurance_plans` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 7: model_versions
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `model_versions` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `model_key` VARCHAR(80) NOT NULL,
  `display_name` VARCHAR(120) NOT NULL,
  `model_type` VARCHAR(40) NOT NULL,
  `file_path` VARCHAR(500) NOT NULL,
  `sha256` CHAR(64) NOT NULL,
  `classes_json` JSON NOT NULL,
  `framework` VARCHAR(80) NOT NULL,
  `framework_version` VARCHAR(40) NOT NULL,
  `is_active` TINYINT(1) NOT NULL DEFAULT 0,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_models_key` (`model_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 8: vehicle_images
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `vehicle_images` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `vehicle_id` BIGINT UNSIGNED NOT NULL,
  `analysis_id` BIGINT UNSIGNED NULL,
  `image_category` VARCHAR(40) NOT NULL DEFAULT 'profile',
  `original_filename` VARCHAR(255) NOT NULL,
  `storage_path` VARCHAR(500) NOT NULL,
  `mime_type` VARCHAR(100) NOT NULL,
  `file_size_bytes` BIGINT NOT NULL,
  `width_px` INT NOT NULL,
  `height_px` INT NOT NULL,
  `sha256` CHAR(64) NOT NULL,
  `is_primary` TINYINT(1) NOT NULL DEFAULT 0,
  `uploaded_by` BIGINT UNSIGNED NULL,
  `uploaded_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_images_vehicle` (`vehicle_id`),
  CONSTRAINT `fk_images_vehicle` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 9: analyses
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `analyses` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `analysis_number` VARCHAR(40) NOT NULL,
  `vehicle_id` BIGINT UNSIGNED NOT NULL,
  `operator_id` BIGINT UNSIGNED NOT NULL,
  `damage_model_version_id` BIGINT UNSIGNED NOT NULL,
  `vehicle_model_version_id` BIGINT UNSIGNED NOT NULL,
  `source_image_id` BIGINT UNSIGNED NOT NULL,
  `annotated_image_path` VARCHAR(500) NULL,
  `status` VARCHAR(30) NOT NULL DEFAULT 'analyzed',
  `damage_confidence` DECIMAL(5,4) NOT NULL,
  `vehicle_confidence` DECIMAL(5,4) NOT NULL,
  `require_vehicle_confirmation` TINYINT(1) NOT NULL DEFAULT 1,
  `vehicle_confirmed` TINYINT(1) NOT NULL,
  `confirmation_overridden` TINYINT(1) NOT NULL DEFAULT 0,
  `override_reason` VARCHAR(500) NULL,
  `raw_prediction_count` INT NOT NULL DEFAULT 0,
  `accepted_damage_count` INT NOT NULL DEFAULT 0,
  `rejected_damage_count` INT NOT NULL DEFAULT 0,
  `subtotal_cost` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
  `tax_amount` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
  `discount_amount` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
  `total_estimated_cost` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
  `currency_code` CHAR(3) NOT NULL DEFAULT 'LKR',
  `operator_notes` TEXT NULL,
  `analyzed_at` DATETIME NULL,
  `finalized_at` DATETIME NULL,
  `finalized_by` BIGINT UNSIGNED NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_analyses_num` (`analysis_number`),
  KEY `idx_analyses_vehicle` (`vehicle_id`),
  KEY `idx_analyses_operator` (`operator_id`),
  KEY `idx_analyses_status` (`status`),
  CONSTRAINT `fk_analyses_vehicle` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`),
  CONSTRAINT `fk_analyses_operator` FOREIGN KEY (`operator_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_analyses_dmg_model` FOREIGN KEY (`damage_model_version_id`) REFERENCES `model_versions` (`id`),
  CONSTRAINT `fk_analyses_veh_model` FOREIGN KEY (`vehicle_model_version_id`) REFERENCES `model_versions` (`id`),
  CONSTRAINT `fk_analyses_image` FOREIGN KEY (`source_image_id`) REFERENCES `vehicle_images` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 10: analysis_vehicle_detections
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `analysis_vehicle_detections` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `analysis_id` BIGINT UNSIGNED NOT NULL,
  `vehicle_class` VARCHAR(60) NOT NULL,
  `confidence` DECIMAL(7,6) NOT NULL,
  `box_json` JSON NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_vdet_analysis` (`analysis_id`),
  CONSTRAINT `fk_vdet_analysis` FOREIGN KEY (`analysis_id`) REFERENCES `analyses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 11: analysis_damages
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `analysis_damages` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `analysis_id` BIGINT UNSIGNED NOT NULL,
  `source` VARCHAR(20) NOT NULL DEFAULT 'model',
  `original_damage_class` VARCHAR(80) NULL,
  `final_damage_class` VARCHAR(80) NOT NULL,
  `vehicle_part` VARCHAR(100) NULL,
  `confidence` DECIMAL(7,6) NULL,
  `box_json` JSON NOT NULL,
  `polygon_json` JSON NULL,
  `model_polygon_json` JSON NULL,
  `mask_refined` TINYINT(1) NOT NULL DEFAULT 0,
  `overlap_ratio` DECIMAL(7,6) NULL,
  `passed_vehicle_gate` TINYINT(1) NOT NULL DEFAULT 1,
  `review_status` VARCHAR(20) NOT NULL DEFAULT 'pending',
  `severity` VARCHAR(20) NOT NULL DEFAULT 'moderate',
  `description` TEXT NULL,
  `internal_note` TEXT NULL,
  `estimated_cost` DECIMAL(15,2) NOT NULL DEFAULT 0.00,
  `reviewed_by` BIGINT UNSIGNED NULL,
  `reviewed_at` DATETIME NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_damages_analysis` (`analysis_id`),
  CONSTRAINT `fk_damages_analysis` FOREIGN KEY (`analysis_id`) REFERENCES `analyses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 12: analysis_revisions
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `analysis_revisions` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `original_analysis_id` BIGINT UNSIGNED NOT NULL,
  `replacement_analysis_id` BIGINT UNSIGNED NOT NULL,
  `reason` TEXT NOT NULL,
  `created_by` BIGINT UNSIGNED NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_revisions_orig` (`original_analysis_id`),
  KEY `idx_revisions_repl` (`replacement_analysis_id`),
  CONSTRAINT `fk_revisions_orig` FOREIGN KEY (`original_analysis_id`) REFERENCES `analyses` (`id`),
  CONSTRAINT `fk_revisions_repl` FOREIGN KEY (`replacement_analysis_id`) REFERENCES `analyses` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 13: reports
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `reports` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `report_number` VARCHAR(50) NOT NULL,
  `analysis_id` BIGINT UNSIGNED NOT NULL,
  `revision_number` INT NOT NULL DEFAULT 1,
  `pdf_path` VARCHAR(500) NOT NULL,
  `sha256` CHAR(64) NOT NULL,
  `snapshot_json` JSON NOT NULL,
  `generated_by` BIGINT UNSIGNED NOT NULL,
  `generated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_current` TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_reports_num` (`report_number`),
  KEY `idx_reports_analysis` (`analysis_id`),
  CONSTRAINT `fk_reports_analysis` FOREIGN KEY (`analysis_id`) REFERENCES `analyses` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 14: company_information
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `company_information` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `company_name` VARCHAR(200) NOT NULL DEFAULT 'Apex Vehicle Assurance Services',
  `registration_number` VARCHAR(100) NOT NULL DEFAULT 'PV-10029384',
  `address_line_1` VARCHAR(255) NOT NULL DEFAULT '100 Commercial Drive',
  `address_line_2` VARCHAR(255) NULL DEFAULT 'Level 4, Apex Tower',
  `city` VARCHAR(100) NOT NULL DEFAULT 'Colombo',
  `phone` VARCHAR(40) NOT NULL DEFAULT '+94 11 234 5678',
  `email` VARCHAR(255) NOT NULL DEFAULT 'claims@apexinsurance.lk',
  `website` VARCHAR(255) NULL DEFAULT 'https://apexinsurance.lk',
  `logo_path` VARCHAR(500) NULL,
  `currency_code` CHAR(3) NOT NULL DEFAULT 'LKR',
  `tax_label` VARCHAR(30) NOT NULL DEFAULT 'VAT',
  `tax_rate` DECIMAL(7,4) NOT NULL DEFAULT 0.1500,
  `report_footer` TEXT NULL,
  `updated_by` BIGINT UNSIGNED NULL,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 15: audit_logs
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `audit_logs` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NULL,
  `action` VARCHAR(100) NOT NULL,
  `entity_type` VARCHAR(80) NOT NULL,
  `entity_id` BIGINT UNSIGNED NULL,
  `old_values_json` JSON NULL,
  `new_values_json` JSON NULL,
  `ip_address` VARCHAR(64) NULL,
  `user_agent` VARCHAR(500) NULL,
  `success` TINYINT(1) NOT NULL DEFAULT 1,
  `failure_reason` VARCHAR(500) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_audit_user` (`user_id`),
  KEY `idx_audit_action` (`action`),
  KEY `idx_audit_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- INITIAL SEED DATA FOR MYSQL
-- =============================================================================

INSERT IGNORE INTO `roles` (`id`, `code`, `name`, `description`) VALUES
(1, 'admin', 'System Administrator', 'Full access to ERP configuration, staff, and audit records.'),
(2, 'operator', 'Claims Operator', 'Registers customers, vehicles, runs analyses, and adds costs.'),
(3, 'customer', 'Policyholder Customer', 'Views owned vehicles, damage summaries, and downloads reports.');

INSERT IGNORE INTO `company_information` (`id`, `company_name`, `registration_number`, `address_line_1`, `address_line_2`, `city`, `phone`, `email`, `website`, `currency_code`, `tax_label`, `tax_rate`, `report_footer`) VALUES
(1, 'Apex Vehicle Assurance Services', 'PV-10029384', '100 Commercial Drive', 'Level 4, Apex Tower', 'Colombo', '+94 11 234 5678', 'claims@apexinsurance.lk', 'https://apexinsurance.lk', 'LKR', 'VAT', 0.1500, 'Official Vehicle Damage Assessment Report produced by Apex Insurance ERP. Advisory only.');

INSERT IGNORE INTO `insurance_plans` (`id`, `plan_code`, `name`, `description`, `coverage_limit`, `deductible_amount`, `currency_code`, `is_active`) VALUES
(1, 'PLN-COMP-GOLD', 'Comprehensive Gold Auto Shield', 'Full comprehensive accident, natural disaster, and third-party liability coverage.', 5000000.00, 15000.00, 'LKR', 1);

-- Initial Admin Account: admin / Admin@123456 (Argon2id hash)
INSERT IGNORE INTO `users` (`id`, `role_id`, `username`, `email`, `password_hash`, `must_change_password`, `is_active`) VALUES
(1, 1, 'admin', 'admin@apexinsurance.lk', '$argon2id$v=19$m=65536,t=3,p=4$ByPB7umY8a/tPEvxfmAa3Q$OYGksqnu0MgbbFG3KCcNpFX60jZGUF1U45FZk4xQONk', 0, 1);
