<?php

/**
 * 诊断脚本：检查环境变量和数据库配置
 */

require __DIR__ . '/vendor/autoload.php';

$app = require_once __DIR__ . '/bootstrap/app.php';
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();

echo "=== 环境变量检查 ===\n";
echo "APP_ENV: " . env('APP_ENV', 'not set') . "\n";
echo "DB_CONNECTION: " . env('DB_CONNECTION', 'not set') . "\n";
echo "DB_HOST: " . env('DB_HOST', 'not set') . "\n";
echo "DB_PORT: " . env('DB_PORT', 'not set') . "\n";
echo "DB_DATABASE: " . env('DB_DATABASE', 'not set') . "\n";
echo "DB_USERNAME: " . env('DB_USERNAME', 'not set') . "\n";
echo "DB_PASSWORD: " . (env('DB_PASSWORD') ? '***' : '(empty)') . "\n";

echo "\n=== 数据库配置检查 ===\n";
$config = config('database.connections.mysql');
echo "Host: " . ($config['host'] ?? 'not set') . "\n";
echo "Port: " . ($config['port'] ?? 'not set') . "\n";
echo "Database: " . ($config['database'] ?? 'not set') . "\n";
echo "Username: " . ($config['username'] ?? 'not set') . "\n";
echo "Password: " . (($config['password'] ?? '') ? '***' : '(empty)') . "\n";

echo "\n=== .env文件检查 ===\n";
$envPath = __DIR__ . '/.env';
if (file_exists($envPath)) {
    echo ".env文件存在\n";
    echo "文件大小: " . filesize($envPath) . " bytes\n";
    echo "文件权限: " . substr(sprintf('%o', fileperms($envPath)), -4) . "\n";
    echo "是否可读: " . (is_readable($envPath) ? 'Yes' : 'No') . "\n";
    
    // 尝试读取前几行（不包含敏感信息）
    $lines = file($envPath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    $dbLines = array_filter($lines, function($line) {
        return strpos($line, 'DB_') === 0 && strpos($line, 'DB_PASSWORD') === false;
    });
    if (!empty($dbLines)) {
        echo "\n找到的DB_配置行:\n";
        foreach (array_slice($dbLines, 0, 5) as $line) {
            echo "  " . $line . "\n";
        }
    } else {
        echo "\n警告: 未找到DB_开头的配置行\n";
    }
} else {
    echo ".env文件不存在\n";
}

echo "\n=== 系统环境变量检查 ===\n";
$systemVars = ['DB_HOST', 'DB_DATABASE', 'DB_USERNAME', 'DB_PASSWORD'];
foreach ($systemVars as $var) {
    $value = getenv($var);
    echo "$var: " . ($value ? ($var === 'DB_PASSWORD' ? '***' : $value) : 'not set') . "\n";
}

