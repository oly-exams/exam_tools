# Admin editor

The admin editor is launched from [exam management](exam_management.md) by clicking on the *edit button*. Only versions having status *Proposal* are editable.


## New Question

A new question contains an empty block *Question*. The exam is then constructed by adding different functional blocks like *Subquestion, Paragraph, etc.* with the *add button*. Each block can have different child blocks. TODO: screen-shot for add-button etc.

## Functional Blocks
Each block has different attributes that define its properties. IMPORTANT: Do not ever change the attribute "id"!

### Question
Main block for every question. Exists only once.

Attributes:
| Key | Specification |
| -------- | -------- |
| points | Total number of points for the whole question. |

Valid children:
* [Title](admin_editor.md#title)
* [Section](admin_editor.md#section)
* [Part](admin_editor.md#part)
* [Subquestion](admin_editor.md#subquestion)
* [Answer](admin_editor.md#answer)
* [Paragraph like blocks](admin_editor.md#paragraph-like-blocks)
* [Box](admin_editor.md#box)
* [Pagebreak](admin_editor.md#pagebreak)
* [Latex blocks](admin_editor.md#latex-blocks)

### Title

Attributes:
| points | Total number of points for the whole question. |

No children.

### Section

No children.

### Part

No children.

### Subquestion

Valid children:
* [Paragraph like blocks](admin_editor.md#paragraph-like-blocks)
* [Latex blocks](admin_editor.md#latex-blocks)

### Answer

Valid children:
* [Paragraph like blocks](admin_editor.md#paragraph-like-blocks)
* [Latex blocks](admin_editor.md#latex-blocks)

### Paragraph like blocks
#### Paragraph

No children.

#### Figure

Valid children:
* [Figure caption](admin_editor.md#figure-caption)

#### Equation

No children.

#### List

Valid children:
* [List item](admin_editor.md#list-item)

#### Table

Valid children:
* [Table row](admin_editor.md#table-row)
* [Table caption](admin_editor.md#table-caption)

#### Box

Valid children:
* [Paragraph like blocks](admin_editor.md#paragraph-like-blocks)
* [Latex blocks](admin_editor.md#latex-blocks)

### Figure Caption

No children.

### List item

No children.

### Table row

Valid children:
* [Table cell](admin_editor.md#table-cell)

### Table cell

No children.

### Table caption

No children.

### Pagebreak

No children.

### Latex Blocks
#### Latex replacement template

Valid children:
* [Latex replacement parameter](admin_editor.md#latex-replacement-parameter)

#### Latex environment

Valid children:
* [Title](admin_editor.md#title)
* [Section](admin_editor.md#section)
* [Part](admin_editor.md#part)
* [Subquestion](admin_editor.md#subquestion)
* [Answer](admin_editor.md#answer)
* [Paragraph like blocks](admin_editor.md#paragraph-like-blocks)
* [Box](admin_editor.md#box)
* [Pagebreak](admin_editor.md#pagebreak)
* [Latex blocks](admin_editor.md#latex-blocks)

### Latex replacement parameter

No children.
