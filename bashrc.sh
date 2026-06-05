function clone() {
    /Users/tejas.patelia/Downloads/Professional/Work/HS-Code/myscript.sh $1 $2
}

function c() {
  git commit -m "$1"
}

function branch() {
  git pull origin master
  git checkout -b $1
}

function ch() {
  git checkout $1
}

function b() {
  git branch
}

function push() {
  git push origin
}

function pull() {
  git pull $1
}

function pullm() {
  git pull origin master
}

function reset() {
  git reset --hard
}
