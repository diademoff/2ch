let posts = document.getElementsByClassName('post');

// "Пост" - "На кого отвечает"
var dict = [];

for (let i = 0; i < posts.length; i++) {
    const post = posts[i];
    // Пост
    post_id = post.id.split('_')[1];

    // На кого отвечает
    post_replies = [];

    replies_links = post.getElementsByClassName('post-reply-link');
    for (let j = 0; j < replies_links.length; j++) {
        const reply = replies_links[j];
        let text = reply.text;
        let reply_id = text.substring(2).split(' ')[0];
        post_replies.push(reply_id)
    }

    dict.push({
        post_id:   post_id, // Пост
        replies: post_replies // На кого отвечает
    });
}

// Конвертировать из "Пост" - "На кого отвечает"
// "Пост" - "Ответы на этот пост"
posts_answers = [];

for (let i = 0; i < dict.length; i++) {
    const post_id = dict[i].post_id;
    answers = [];

    for (let j = 0; j < dict.length; j++) {
        // На кого отвечает
        const replies_on = dict[j].replies;
        if (replies_on.includes(post_id)) {
            answers.push(dict[j].post_id);
            continue;
        }
    }

    posts_answers.push({
        post_id: post_id,
        answers: answers
    });
}

// Заполнить боковое меню
let dashboard = document.getElementById('dashboard');

function get_link(post_id, prefix){
    var link = document.createElement("a");
    link.textContent = prefix + post_id;
    link.href = '#post_' + post_id;
    return link;
}

// Функция для рекурсивного заполнения ответов
function print_answers(answers, prefix){
    for (let i = 0; i < answers.length; i++) {
        const answer = answers[i];
        printed_as_answers.push(answer);
        dashboard.appendChild(get_link(answer, prefix));
        print_answers(get_answers_for(answer), prefix + '> ') // of answer
    }
}

// Получить ответы на пост с заданным айди
function get_answers_for(post_id){
    for (let i = 0; i < posts_answers.length; i++) {
        const id = posts_answers[i].post_id;
        if (id === post_id){
            return posts_answers[i].answers;
        }

    }
}

let printed_as_answers = [];
let prefix = '';

for (let i = 0; i < posts_answers.length; i++) {
    const post_id = posts_answers[i].post_id;
    const answers = posts_answers[i].answers;

    if (printed_as_answers.includes(post_id)) {
        continue;
    }

    dashboard.appendChild(get_link(post_id, ''));

    print_answers(answers, '> ')
}

