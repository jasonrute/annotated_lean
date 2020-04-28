# Annotated Lean Files

## [Click here to see annotated Lean files](index.md)

... or read below for more about this project.

## What is this?

The [Lean 3 theorem prover](https://leanprover.github.io/) (now maintained by the [leanprover-community](https://leanprover-community.github.io/)) provides a language server used by Emacs and VS Code.  This language server provides the usual language server features (the ability to jump to a definition, see a doc string, or see the type of a declaration).  It also provides some features specific to tactic-based theorem proving such as the ability to see the proof state at any stage of the proof.

This project is a simple way to visualize all the information present in a lean file that the Lean server uses.  It grew out of [another project](https://github.com/jasonrute/lean_info_scrapper) to scrape all the information from the Lean language server (by running an "info" command at every character in the Lean file).  Here we take that infomation and make it pretty looking for easy inspection.

## Types of information

- **full-id**: The full name of a declaration.
- **source**: The location (file, line, and column) where a declaration is defined.  Can be used to jump to that definition.
- **type**: The type of a function, variable, etc.  As a dependently typed language, this is incredibly important information.
- **doc**: The doc string associated with a definition.
- **text**: For tactics, this is the name of the tactic, e.g. "exact".
- **tactic_params**: The different types of parameters that a tactic can take.
- **tactic_param_ix**: The index for this paramater of the tactic.
- **state**: The Lean goal state.  (These files are generated using pp.all=True, so the goal state is more verbose than usual.)

## How to read this

In the HTML files, each code line is followed by zero or more lines of symbols, one for each type of information present in that code line.  For example:
```
  8  import algebra.group data.multiset
src         └───────────┘ └───────────┘
```
means that on line 8 there is source information for `algebra.group` and `data.multiset` and that every character in those strings have the same source information.

You can see the information for that block by hovering over `└───────────┘`.

The `┴` character is used when the information only spans one character.
```
 14  def is_unit [monoid α] (a : α) : Prop := ∃u:units α, a = u
id                └────┘ ┴       ┴            ┴  └───┘ ┴┴ ┴ ┴ ┴
```

Some code lines have lots of information and sometimes the blocks can span multiple lines of code.
```
 47  by simp [is_unit_iff_exists_inv, mul_comm]
id            └────────────────────┘  └──────┘
src     └────┘└────────────────────┘└┘└──────┘└─
typ     └────┘└────────────────────┘└┘└──────┘└─
doc     └────┘                      └┘        └─
txt     └────┘                      └┘        └─
par     └────┘                      └┘        └─
pid         ┴┴                      └┘        ┴└
st     └────────────────────────────────────────
 48  
src  ┘
typ  ┘
doc  ┘
txt  ┘
par  ┘
pid  ┘
st   ┘
```

## How to view these files

Github won't render HTML files, so use [https://htmlpreview.github.io/?](https://htmlpreview.github.io/?).  If you start at [the index here](index.md) you should be fine.

  Monospace fonts are hard.  Some unicode characters might throw off the alignment.  Hopefully it is viewable on most operating systems and browsers.
  
## Quirks

There are two types of quirks.  The first are quirks with my extraction method.  Some files, such as [topology/metric/space/gromov_hausdorff_realized](https://htmlpreview.github.io/?https://github.com/jasonrute/annotated_lean/blob/master/html/topology__metric_space__gromov_hausdorff_realized.html) are missing a lot of the annotations.  Improvements to the extraction code, using the new [Lean client for Python](https://github.com/leanprover-community/lean-client-python) should hopefully clear up these issues.

The second are quirks with the Lean server itself.  Here are a few of many

- It is not always true that every character in a continuous string of letters has the same information.  For example, in [algebra/archimedean.lean](https://htmlpreview.github.io/?https://github.com/jasonrute/annotated_lean/blob/master/html/algebra__archimedean.html) notice that the projection notation `.imp` doesn't get information for the final `p`.  I assume this is a small bug in the Lean server.  
    ```
    145    (H (x / y)).imp $ λ n h, le_of_lt $
    id      ┴  ┴ ┴ ┴  └─┘      ┴ ┴  └──────┘
    src          ┴    └─┘           └──────┘
    typ     ┴  ┴ ┴ ┴  └─┘      ┴ ┴  └──────┘
    ``` 
- Also, if one browses these files one can quickly see that it isn't clearly obvious how to extract information (such as, say, finding all tactic instances and their goal states).  There are a lot of quirks, especially when one starts including `by` blocks inside `begin...end` blocks in term mode inside another `begin...end` block, say.

## Script

I've provided some Python scripts for creating these files.  They require data generated by the [Lean info scraper](https://github.com/jasonrute/lean_info_scrapper).  Run as 
```bash
python3 scripts/generate_html.py /the/path/to/the/scraped/data/files/ /the/path/to/mathlib/src/ /the/path/to/lean/library/ html/

python3 scripts/generate_index.py /the/path/to/the/scraped/data/files/ https://github.com/jasonrute/annotated_lean html/ index.md
```