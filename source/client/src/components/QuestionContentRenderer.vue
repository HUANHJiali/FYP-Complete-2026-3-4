<template>
  <div class="question-content-renderer" :class="{ compact }">
    <template v-for="(block, index) in parsedBlocks" :key="index">
      <p v-if="block.type === 'text'" class="qcr-text">{{ block.content }}</p>

      <div v-else-if="block.type === 'formula'" class="qcr-formula">
        {{ block.content }}
      </div>

      <div v-else-if="block.type === 'image'" class="qcr-image-wrap">
        <img class="qcr-image" :src="block.src" :alt="block.alt || 'image'" />
      </div>

      <div v-else-if="block.type === 'table'" class="qcr-table-wrap">
        <table class="qcr-table">
          <thead>
            <tr>
              <th v-for="(head, hIdx) in block.headers" :key="hIdx">{{ head }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rIdx) in block.rows" :key="rIdx">
              <td v-for="(cell, cIdx) in row" :key="cIdx">{{ cell }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script>
export default {
  name: 'QuestionContentRenderer',
  props: {
    content: {
      type: [String, Number],
      default: ''
    },
    compact: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    parsedBlocks() {
      const text = (this.content == null ? '' : String(this.content)).replace(/\r\n/g, '\n')
      if (!text.trim()) return [{ type: 'text', content: '' }]

      const lines = text.split('\n')
      const blocks = []
      let idx = 0

      while (idx < lines.length) {
        const line = lines[idx].trim()

        if (!line) {
          idx += 1
          continue
        }

        const imageBlock = this.parseImage(line)
        if (imageBlock) {
          blocks.push(imageBlock)
          idx += 1
          continue
        }

        if (line.startsWith('$$')) {
          const formulaLines = [line]
          idx += 1
          while (idx < lines.length && !lines[idx].trim().endsWith('$$')) {
            formulaLines.push(lines[idx])
            idx += 1
          }
          if (idx < lines.length) {
            formulaLines.push(lines[idx].trim())
            idx += 1
          }
          blocks.push({ type: 'formula', content: formulaLines.join('\n') })
          continue
        }

        if (this.isTableHeader(lines, idx)) {
          const table = this.parseTable(lines, idx)
          blocks.push(table.block)
          idx = table.nextIndex
          continue
        }

        blocks.push({ type: 'text', content: lines[idx] })
        idx += 1
      }

      return blocks.length > 0 ? blocks : [{ type: 'text', content: text }]
    }
  },
  methods: {
    parseImage(line) {
      const markdownImage = line.match(/^!\[(.*?)\]\((https?:\/\/[^\s)]+)\)$/i)
      if (markdownImage && this.isSafeImageUrl(markdownImage[2])) {
        return {
          type: 'image',
          alt: markdownImage[1],
          src: markdownImage[2]
        }
      }

      const rawImage = line.match(/^(https?:\/\/\S+\.(png|jpg|jpeg|gif|webp|svg))(\?\S+)?$/i)
      if (rawImage && this.isSafeImageUrl(line)) {
        return {
          type: 'image',
          alt: '',
          src: line
        }
      }

      return null
    },
    isSafeImageUrl(url) {
      return /^https?:\/\//i.test(url)
    },
    isTableHeader(lines, idx) {
      if (idx + 1 >= lines.length) return false
      const header = lines[idx]
      const separator = lines[idx + 1]
      return header.includes('|') && /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(separator)
    },
    parseTable(lines, startIdx) {
      const headers = this.splitTableLine(lines[startIdx])
      let idx = startIdx + 2
      const rows = []

      while (idx < lines.length && lines[idx].includes('|') && lines[idx].trim()) {
        rows.push(this.splitTableLine(lines[idx]))
        idx += 1
      }

      return {
        block: {
          type: 'table',
          headers,
          rows
        },
        nextIndex: idx
      }
    },
    splitTableLine(line) {
      return line
        .trim()
        .replace(/^\|/, '')
        .replace(/\|$/, '')
        .split('|')
        .map(item => item.trim())
    }
  }
}
</script>

<style scoped>
.question-content-renderer {
  line-height: 1.8;
  color: #262626;
}

.qcr-text {
  white-space: pre-wrap;
  margin: 0 0 8px;
}

.qcr-formula {
  background: #f6f8fa;
  border-radius: 6px;
  padding: 8px 10px;
  white-space: pre-wrap;
  margin-bottom: 8px;
  font-family: "Consolas", "Monaco", monospace;
}

.qcr-image-wrap {
  margin: 8px 0;
}

.qcr-image {
  max-width: 100%;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
}

.qcr-table-wrap {
  overflow-x: auto;
  margin: 8px 0;
}

.qcr-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #e8e8e8;
  background: #fff;
}

.qcr-table th,
.qcr-table td {
  border: 1px solid #e8e8e8;
  padding: 6px 8px;
  text-align: left;
}

.qcr-table th {
  background: #fafafa;
}

.question-content-renderer.compact {
  font-size: 12px;
  line-height: 1.6;
}
</style>
