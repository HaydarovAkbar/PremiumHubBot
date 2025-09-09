from telegraph import Telegraph

telegraph = Telegraph()
telegraph.create_account(short_name='bonus')

video_url = "https://premium24.uz/static/videos/stories.mp4"

response = telegraph.create_page(
    title='🎥 Video',
    html_content=f'''
        <p><a href="{video_url}">📽 Videoni ko‘rish</a></p>
    '''
)

print("Telegra.ph sahifasi:", response['url'])
