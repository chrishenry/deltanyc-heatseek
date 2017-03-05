FROM ruby:2.3.3

RUN apt-get update -qq && \
    apt-get install -y build-essential libpq-dev nodejs nodejs-legacy npm && \
    npm install -g phantomjs-prebuilt bower && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /angular-rails-app
WORKDIR /angular-rails-app

ADD Gemfile /angular-rails-app/Gemfile
ADD Gemfile.lock /angular-rails-app/Gemfile.lock
RUN bundle install
ADD . /angular-rails-app