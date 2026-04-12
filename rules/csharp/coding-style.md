---
paths:
  - "**/*.cs"
  - "**/*.csproj"
---
# C# Coding Style

> This file extends [common/coding-style.md](../common/coding-style.md) with C# specific content.

## Formatting

- Allman 风格大括号（换行放置）
- `foreach`/`for`/`if`/`while` 等控制语句必须使用大括号，禁止省略
- 多语句块（如 `if` 内含 `break`/`return`）必须大括号换行，禁止写成单行
- 单表达式属性/方法使用 `=>` 表达式体，如 `public int m_Hp => _hp;`，禁止 `{ get { return _hp; } }` 写法
- 避免过度换行，大于 120 字符时才考虑换行
- 注释仅用于解释 why（为什么这样做），不注释 what（代码在做什么）——代码本身应自解释

## Type Inference

- 右侧类型已明确时必须用 `var`（如 `new`、强制转换、泛型方法返回），禁止左右两侧重复写类型

## Naming

- 私有字段：`_camelCase`
- 公共字段（基本类型）：`m_类型标识符PascalCase`，如 `m_iCounter`、`m_uGuid`、`m_bIsValid`、`m_fRatio`、`m_dSpeed`、`m_sName`
- 公共字段（引用/指针类型）：`m_p` + PascalCase，如 `m_pOwner`、`m_pTarget`
- 公共字段（列表）：`m_ls` + PascalCase，如 `m_lsBuffList`
- 公共字段（字典）：`m_dic` + PascalCase，如 `m_dicPlayerData`
- 公共字段（其他类型）：`m_camelCase`，如 `m_customer`
- 常量：`PascalCase`
- 方法/属性：`PascalCase`
- 参数/局部变量：`camelCase`

## AI Behavior

- 如无授权，**禁止** 自动写各种测试用例
- 如无授权，**禁止** 在代码中写入"新增..."、"原有..."等注释
- 如无授权，**禁止** 自动写各种备用、fallback 方案

## Error Handling

- 使用具体异常类型，避免 `catch (Exception)`
- 字符串判空使用 `string.IsNullOrEmpty(s)`，禁止 `s == null` 或 `s == ""`
