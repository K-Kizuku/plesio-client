---
name: 'DD'
root: '.'
output: './docs/DesignDoc'
ignore: ['.']
questions:
  number: 'バージョン管理'
  fileName: '何の機能のDDか教えてね'

---

# `{{ inputs.number | rtrim }}_{{ inputs.fileName }}.md`

```markdown
# DesignDoc

```