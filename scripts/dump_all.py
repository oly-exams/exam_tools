#!/usr/bin/env python

import sys
import os
import os.path

if __name__ == "__main__":
    output_dir = sys.argv[1]
    try:
        os.makedirs(output_dir)
    except:
        pass

    fn = os.path.join(output_dir, "999_fulldump.json")
    os.system(
        f'python manage.py dumpdata --natural-foreign --natural-primary --indent=2 --exclude auth.permission --exclude contenttypes --exclude admin --exclude djcelery --exclude sessions --exclude ipho_core.PushSubscription --exclude ipho_exam.Figure --exclude ipho_exam.CompiledFigure --exclude ipho_exam.RawFigure > "{fn}"'
    )

    os.system(f'python scripts/export_figures.py "{output_dir}"')
