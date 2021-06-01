let posts = document.getElementsByClassName('post');

// "Пост" - "На кого отвечает"
var dict = [];

for (let i = 0; i < posts.length; i++) {
    const post = posts[i];
    // Пост
    post_id = post.id.split('_')[1];

    // На кого отвечает
    post_replies = [];
    let replies_count = 0;

    replies_links = post.getElementsByClassName('post-reply-link');
    for (let j = 0; j < replies_links.length; j++) {
        const reply = replies_links[j];
        let text = reply.text;
        let reply_id = text.substring(2).split(' ')[0];
        post_replies.push(reply_id)
        replies_count += 1;
    }

    dict.push({
        post_id: post_id, // Пост
        replies: post_replies, // На кого отвечает
        replies_count: replies_count
    });
}

// Конвертировать из "Пост" - "На кого этот пост отвечает"
// в "Пост" - "Ответы на этот пост"
posts_answers = [];

for (let i = 0; i < dict.length; i++) {
    const post_id = dict[i].post_id;
    answers = [];

    for (let j = 0; j < dict.length; j++) {
        const replies_on = dict[j].replies;
        if (replies_on.includes(post_id)) {
            answers.push(dict[j].post_id);
            continue;
        }
    }

    posts_answers.push({
        post_id: post_id,
        answers: answers,
    });
}

function post_answering_on_count(post_id) {
    for (let i = 0; i < dict.length; i++) {
        const element = dict[i];
        if (post_id == element.post_id) {
            return element.replies_count;
        }
    }
}

// Заполнить боковое меню
let dashboard = document.getElementById('dashboard');

// Получить элемент ссылки для меню навигации
function get_link(post_id, prefix) {
    var link = document.createElement("a");
    postfix = '';
    if (post_answering_on_count(post_id) > 10) {
        // Пост считается спамом если отвечает
        // более чем на 10 постов
        postfix += ' (spam)';
        link.classList.add('spam')
    }
    link.textContent = prefix + post_id + postfix;
    link.href = '#post_' + post_id;
    return link;
}

// Функция для рекурсивного заполнения ответов
function print_answers(answers, prefix) {
    for (let i = 0; i < answers.length; i++) {
        const answer = answers[i];
        printed_as_answers.push(answer);
        dashboard.appendChild(get_link(answer, prefix));
        // Рекурсивный вызов с изменением префикса
        print_answers(get_answers_for(answer), prefix + '> ')
    }
}

// Получить ответы на пост с заданным айди
function get_answers_for(post_id) {
    for (let i = 0; i < posts_answers.length; i++) {
        const id = posts_answers[i].post_id;
        if (id === post_id) {
            return posts_answers[i].answers;
        }
    }
}

let printed_as_answers = [];

for (let i = 0; i < posts_answers.length; i++) {
    const post_id = posts_answers[i].post_id;
    const answers = posts_answers[i].answers;

    if (printed_as_answers.includes(post_id)) {
        continue;
    }

    // Вывести номер текущего поста
    dashboard.appendChild(get_link(post_id, ''));

    // Вывести ответы на этот пост рекурсивно
    print_answers(answers, '> ')
}

// Заменить ссылки
for (let i = 0; i < posts.length; i++) {
    const post = posts[i];
    replies_links = post.getElementsByClassName('post-reply-link');
    for (let j = 0; j < replies_links.length; j++) {
        const reply = replies_links[j];
        let text = reply.text;
        let reply_id = text.substring(2).split(' ')[0];
        replies_links[j].href = "#post_" + reply_id;
    }

    // Добавить footer ответы
    footer = post.getElementsByClassName('post_footer')[0];
    answers_for_current = get_answers_for(posts[i].id.split('_')[1])

    for (let i = 0; i < answers_for_current.length; i++) {
        const element = answers_for_current[i];

        let curr_link = get_link(element, '>>')

        footer.appendChild(curr_link);
    }
}