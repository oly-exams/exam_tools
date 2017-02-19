# Admin editor

The admin editor is launched from [exam management](exam_management.md) by clicking on the *edit button*. Only versions having status *Proposal* are editable.


## New Question

A new question contains an empty block *Question*. The exam is then constructed by adding different functional blocks like *Subquestion, Paragraph, etc.* with the *add button*. Each block can have different child blocks. TODO: screen-shot for add button etc.

## Functional Blocks
### Question
Main block for every question. Exists only once.

Valid children:
* [Title](admin_editor.md#title)
* [Section]("section")
* [Part]("part")
* [Subquestion]("subquestion")
* [Answer]("answer")
* [Paragraph like blocks]("paragraph-like-blocks")
* [Box]("box")
* [Pagebreak]("pagebreak")
* [Latex blocks]("latex-blocks")

### Title

No children.

### Section

No children.

### Part

No children.

### Subquestion

Valid children:
* [Paragraph like blocks]("paragraph-like-blocks")
* [Latex blocks]("latex-blocks")

### Answer

Valid children:
* [Paragraph like blocks]("paragraph-like-blocks")
* [Latex blocks]("latex-blocks")

### Paragraph like blocks
#### Paragraph

No children.

#### Figure

Valid children:
* [Figure caption]("figure-caption")

#### Equation

No children.

#### List

Valid children:
* [List item]("list-item")

#### Table

Valid children:
* [Table row]("table-row")
* [Table caption]("table-caption")

#### Box

Valid children:
* [Paragraph like blocks]("paragraph-like-blocks")
* [Latex blocks]("latex-blocks")

### Figure Caption

No children.

### List item

No children.

### Table row

Valid children:
* [Table cell]("table-cell")

### Table cell

No children.

### Table caption

No children.

### Pagebreak

No children.

### Latex Blocks
#### Latex replacement template

Valid children:
* [Latex replacement parameter]("latex-replacement-parameter")

#### Latex replacement parameter

No children.

#### Latex environment

Valid children:
* [Title]("title")
* [Section]("section")
* [Part]("part")
* [Subquestion]("subquestion")
* [Answer]("answer")
* [Paragraph like blocks]("paragraph-like-blocks")
* [Box]("box")
* [Pagebreak]("pagebreak")
* [Latex blocks]("latex-blocks")


