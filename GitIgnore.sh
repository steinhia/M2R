find ./* -size +30M | cat > .gitignore
sort .gitignore | uniq -u
echo '*.wav' >> .gitignore
echo '*.tak' >> .gitignore
echo '*.swp' >> .gitignore
echo '*.mp4' >> .gitignore
echo '*.zip' >> .gitignore
echo '*.tar*' >> .gitignore
echo '*.c3d*' >> .gitignore
echo '*.png*' >> .gitignore
echo '*.avi*' >> .gitignore
echo '*.jpg*' >> .gitignore
echo '*.xcf*' >> .gitignore
