import downloader
import reddit

version = 1.0

print(f"\nYou are running version {version}")


def GetChapters():
    # get content
    content = reddit.getContent()
    # download content
    if content != {}:
        downloader.download(content)
    # prompt
    print("\nDone!")


if __name__ == "__main__":
    # get and save one piece chapters
    GetChapters()
