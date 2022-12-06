#!/usr/bin/env bash

set -ex

perl -spi -e 's=True=False=' ~/.halform/hop_test

rm -rf hop_test
set +e
dropdb hop_test
set -e

yes | hop new hop_test

cd hop_test

tree .

hop
perl -spi -e 's=False=True=' ~/.halform/hop_test
echo 'IN PRODUCTION'
hop
perl -spi -e 's=True=False=' ~/.halform/hop_test


git remote add origin git@gite.lirmm.fr:maizi/tmptest.git
git push -uf origin hop_main

hop prepare-patch -l patch -m "First import"

echo 'create table a ( a text primary key )' > Patches/0/0/1/a.sql
echo 'print("I am a script without x permission...")' > Patches/0/0/1/a.py

hop apply-patch

tree .

hop

yes | hop apply-patch

hop apply-patch -f

git add .
git commit -m "(wip) First"
git status

echo 'create table a ( a text primary key, bla text )' > Patches/0/0/1/a.sql

hop undo-patch

hop apply-patch
git diff hop_test/public/a.py

git status
git hist

set +e
# should commit before release
hop release-patch
set -e

git add .
git commit -m "(wip) ajout de a.bla"

touch dirty
set +e
# git repo must be clean
hop release-patch
set -e
rm dirty

echo '        verybad' >> hop_test/public/a.py
git add .
git commit -m "(bad)"
set +e
# git repo must be clean
hop release-patch
set -e
git reset HEAD~ --hard

hop release-patch --push

git status

# echo 'APPLY PATCH IN PRODUCTION'
# git checkout hop_0.0.1
# hop undo-patch -d
# git checkout hop_main

# perl -spi -e 's=False=True=' ~/.halform/hop_test

# hop

# hop apply-patch

# perl -spi -e 's=True=False=' ~/.halform/hop_test

# mv ../../half_orm_packager/version.txt ../../half_orm_packager/version.txt.o

# echo '0.1.0' > ../../half_orm_packager/version.txt

hop

hop prepare-patch -l patch -m "Second import"

echo 'create table b ( b text primary key, a text references a )' > Patches/0/0/2/b.sql

hop apply-patch

tree

# git diff
git status

git add .
git commit -m "(wip) Second"

cat > hop_test/public/b.py << EOF
# hop release: 0.1.0
# pylint: disable=wrong-import-order, invalid-name, attribute-defined-outside-init

"""The module hop_test.public.b povides the B class.

WARNING!

This file is part of the hop_test package. It has been generated by the
command hop. To keep it in sync with your database structure, just rerun
hop update.

More information on the half_orm library on https://github.com/collorg/halfORM.

DO NOT REMOVE OR MODIFY THE LINES BEGINING WITH:
#>>> PLACE YOUR CODE BELOW...
#<<< PLACE YOUR CODE ABOVE...

MAKE SURE YOUR CODE GOES BETWEEN THESE LINES OR AT THE END OF THE FILE.
hop ONLY PRESERVES THE CODE BETWEEN THESE MARKS WHEN IT IS RUN.
"""

from hop_test.db_connector import base_relation_class

#>>> PLACE YOUR CODE BELLOW THIS LINE. DO NOT REMOVE THIS LINE!
import datetime
#<<< PLACE YOUR CODE ABOVE THIS LINE. DO NOT REMOVE THIS LINE!

__RCLS = base_relation_class('public.b')

class B(__RCLS):
    """
    __RCLS: <class 'half_orm.model.Table_Hop_testPublicB'>
    This class allows you to manipulate the data in the PG relation:
    TABLE: "hop_test":"public"."b"
    FIELDS:
    - b: (text) NOT NULL
    - a: (text)

    PRIMARY KEY (b)
    FOREIGN KEY:
    - b_a_fkey: ("a")
     ↳ "hop_test":"public"."a"(a)

    To use the foreign keys as direct attributes of the class, copy/paste the Fkeys bellow in
    your code as a class attribute and replace the empty string(s) key(s) with the alias you
    want to use. The aliases must be unique and different from any of the column names. Empty
    string keys are ignored.

    Fkeys = {
        '': 'b_a_fkey',
    }
    """
    #>>> PLACE YOUR CODE BELLOW THIS LINE. DO NOT REMOVE THIS LINE!
    Fkeys = {
        'a_fk': 'b_a_fkey',
    }
    #<<< PLACE YOUR CODE ABOVE THIS LINE. DO NOT REMOVE THIS LINE!
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #>>> PLACE YOUR CODE BELLOW THIS LINE. DO NOT REMOVE THIS LINE!
EOF

git add .
git commit -m "(b) with Fkeys"

hop release-patch

git status
git push
git tag
