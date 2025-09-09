from telegraph import Telegraph

telegraph = Telegraph()
telegraph.create_account(short_name='bonus')

video_url = "https://premium24.uz/static/videos/stories.mp4"  # <-- serveringizdagi real video manzili

response = telegraph.create_page(
    title='🎥',  # title zarur, lekin minimal belgili bo'lishi mumkin
    html_content=f'''
        <video controls width="100%">
            <source src="{video_url}" type="video/mp4">
        </video>
    '''
)

print("Telegra.ph sahifasi:", response['url'])
