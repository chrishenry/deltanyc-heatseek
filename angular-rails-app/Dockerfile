FROM ruby:2.3.3

RUN apt-get update -qq && \
    apt-get install -y build-essential libpq-dev nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /rails-app
WORKDIR /rails-app

ADD Gemfile /rails-app/Gemfile
ADD Gemfile.lock /rails-app/Gemfile.lock
RUN bundle install
ADD . /rails-app
