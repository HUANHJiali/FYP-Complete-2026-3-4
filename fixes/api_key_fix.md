# 修复硬编码API密钥

## 步骤1: 编辑docker-compose.yml

将:
```yaml
environment:
  - ZHIPUAI_API_KEY=fd4abef3ba11457eba10ad862d2b3ec2.PCPLHkU12JIB3aIf
```

改为:
```yaml
environment:
  - ZHIPUAI_API_KEY=${ZHIPUAI_API_KEY}
```

## 步骤2: 更新.env文件

将:
```
ZHIPUAI_API_KEY=your_api_key_here
```

改为:
```
ZHIPUAI_API_KEY=你的真实API密钥
```

## 步骤3: 重启服务

```bash
docker-compose down
docker-compose up -d
```
