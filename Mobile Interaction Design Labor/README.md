<img width="315" alt="Screenshot 2024-03-25 at 12 14 09" src="https://github.com/citrusqwq/master/assets/66939444/d8d80f1e-af92-43e2-b206-d4848319d476">
<img width="314" alt="Screenshot 2024-03-25 at 12 14 20" src="https://github.com/citrusqwq/master/assets/66939444/fe77ac9a-da92-4550-a68c-da62aee1c9bf">
<img width="311" alt="Screenshot 2024-03-25 at 12 14 34" src="https://github.com/citrusqwq/master/assets/66939444/5a36da61-fb22-4551-8d02-9cc7b714fd8c">
<img width="309" alt="Screenshot 2024-03-25 at 12 14 54" src="https://github.com/citrusqwq/master/assets/66939444/6eae2172-225c-42e8-ac4c-07bbab6cc784">
<img width="312" alt="Screenshot 2024-03-25 at 12 15 12" src="https://github.com/citrusqwq/master/assets/66939444/6d6398cf-acef-4347-8c56-a9fdf132869f">
<img width="313" alt="Screenshot 2024-03-25 at 12 15 52" src="https://github.com/citrusqwq/master/assets/66939444/1dbd8898-da8e-4775-b71d-006be502e644">



# Peek-A-Read
Our project consisted of creating an Android app that uses text recognition to make text adjustable to individual needs. Regardless of how good our eyesight might be, we all have encountered text that has been difficult to read -because it was either too small or the contrast of text and background color wasn’t optimal.
Peek-A-Read allows the user to take a picture of the illegible text, and the app then highlights the recognized text. The user may then select the area to be read, adjust font and size if needed, as well as choose whether the text should be read out loud, using the Text-to-Speech button. All of these features in only two screens with minimal buttons and icons. Our goal was to keep the design as simple as possible to make it intuitive and easy to use, even considering the target group of the app.

The main target group is visually impaired people or seniors who would benefit from using the app to make any text better legible for them. Alternatively, Peek-A-Read can be used to read any small text (such as instruction manuals or package inserts) considered challenging to read by the average user, as well as a simple alternative to other Text-to-Speech apps.

Our approach is to have users take pictures using a simple built-in camera with the option to enable the flashlight when taking a picture. This built-in camera is simple enough that even individuals without a technical background can easily get started with our app. We could enhance the camera's features by adding options like zoom-in, focus, etc. This alternative would allow users to capture better pictures, improving text recognition accuracy in subsequent stages. Additionally, we could allow picture selection from the gallery, in which case users can not only read text from self-taken photos but also pictures saved from other sources. While both alternatives could make our app more versatile, considering our target user group—people with visual impairments—many may face difficulty using a cell phone. As a result, we decided to stick with the simple built-in camera, which we believe is the most user-friendly approach.
For text recognition, displaying all recognized text at once might overwhelm users with a large amount of unordered text. Since Google ML-Kit returns recognition results in blocks, lines, and elements, we opted to let users choose which recognized blocks they want to read. This way, text belonging to the same paragraph can be read together.

Latest APK: https://seafile.cloud.uni-hannover.de/f/e33e2b1c6a8c46fb81fa/?dl=1

