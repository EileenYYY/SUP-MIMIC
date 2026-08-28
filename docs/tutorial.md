# Tutorial

下面是一条从零到一的标准使用路线，覆盖数据提取、病例构建、统计分析和机器学习 baseline。

## 0. 先准备数据库

确认 MIMIC 已经按官方方式加载到 PostgreSQL，且 schema 可访问：

- `mimiciv_hosp`
- `mimiciv_icu`
- `mimiciv_derived`
- `mimiciv_ed`
- `mimiciv_note`（如果你要处理 notes）

## 1. 安装项目

```bash
pip install -e .[dev,postgres]
```

## 2. 配置连接

编辑 `configs/example_config.yaml`，把：

```yaml
database:
  dsn: ${SUP_MIMIC_DATABASE_DSN}
```

改成你的真实连接串。

## 3. 先验证配置

```bash
mimic-pipeline validate-config --config configs/example_config.yaml
```

这一步会检查：

- YAML 是否能读
- jobs 是否完整
- 路径是否可解析

## 4. 执行提取

```bash
mimic-pipeline run --config configs/example_config.yaml --subject-id YOUR_SUBJECT_ID --hadm-id YOUR_HADM_ID --stay-id YOUR_STAY_ID
```

运行后会生成：

- `outputs/raw/patients.jsonl`
- `outputs/raw/admissions.jsonl`
- `outputs/raw/icustays.jsonl`
- `outputs/raw/first_day_labs.jsonl`
- `outputs/raw/first_day_vitals.jsonl`
- `outputs/raw/diagnoses.jsonl`
- `outputs/raw/procedures.jsonl`
- `outputs/raw/prescriptions.jsonl`

## 5. 构建病例档案

```bash
mimic-pipeline build-case --config configs/example_config.yaml --input-dir outputs/raw --output outputs/cases/case_profile.json
```

这个步骤会把多表结果拼成一个 patient-level JSON。

## 6. 应用筛选

```bash
mimic-pipeline screen --config configs/example_config.yaml --input outputs/cases/case_profile.json --output outputs/cases/screened.json
```

筛选规则通常用于：

- 排除不完整病例
- 排除 newborn
- 过滤年龄过低样本
- 限制 ICU 轨迹是否必须存在

## 7. 生成 feature table

```bash
mimic-pipeline build-features --input outputs/cases/case_profile.json --output outputs/features.csv
```

这个步骤会把嵌套病例对象展开成可训练的特征表。

## 8. 做描述统计

```bash
mimic-pipeline stats-summary --input outputs/cases/case_profile.json --output outputs/reports/case_summary.json
```

你也可以对某个字段做频数统计：

```bash
mimic-pipeline stats-summary --input outputs/raw/admissions.jsonl --field admission_type --output outputs/reports/admission_type.json
```

## 9. 训练 baseline 模型

```bash
mimic-pipeline train-model --input outputs/features.csv --model-output outputs/models/baseline.pkl --metrics-output outputs/models/baseline_metrics.json
```

需要输入带标签的特征表，标签默认是 `__label__`。

## 10. 评估模型

```bash
mimic-pipeline evaluate-model --input outputs/features.csv --model outputs/models/baseline.pkl --output outputs/models/baseline_eval.json
```

## 11. 检查输出

重点看三类东西：

- 行数是否符合预期
- 时间字段是否稳定
- 关键字段是否缺失

## 12. 如何扩展到新数据类型

如果你想加 `notes`：

1. 新建 SQL
2. 在 `configs/example_config.yaml` 里加一个 job
3. 在 `builders.py` 里把 notes 接入 case profile
4. 在 `docs/data_dictionary.md` 里补一行
5. 在 `tests/` 里补一个最小样例

如果你想加一个机器学习任务：

1. 先准备标签字段
2. 用 `build-features` 做特征表
3. 用 `train-model` 跑 baseline
4. 再替换成更复杂的模型

## 13. 推荐的发布顺序

1. 先发布 SQL + docs
2. 再发布 Python 工具
3. 再加筛选规则
4. 最后加 benchmark/task layer
5. 再补统计和 ML baseline
