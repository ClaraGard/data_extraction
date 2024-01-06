from sqlalchemy import create_engine, ForeignKey, Column, String, INTEGER, DateTime, Text, Table
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

from datetime import datetime
Base = declarative_base()

PostLink = Table(
    'post_link',
    Base.metadata,
    Column('post_id', INTEGER, ForeignKey('post.id'), primary_key=True),
    Column('link_id', INTEGER, ForeignKey('link.id'), primary_key=True)
)

PostImage = Table(
    'post_image',
    Base.metadata,
    Column('post_id', INTEGER, ForeignKey('post.id'), primary_key=True),
    Column('image_id', INTEGER, ForeignKey('image.id'), primary_key=True)
)

class Link(Base):
    __tablename__ = 'link'
    id = Column(INTEGER, primary_key=True)
    link = Column(String, nullable=False, unique=True)
    posts = relationship('post', secondary=PostLink, back_populates='link')

class Image(Base):
    __tablename__ = 'image'
    id = Column(INTEGER, primary_key=True)
    link = Column(String, nullable=False, unique=True)
    posts = relationship('post', secondary=PostImage, back_populates='image')


class Post(Base):
    __tablename__ = "post"
    id = Column(INTEGER, primary_key=True)
    link = Column(String(1000), nullable=False, unique=True)
    date = Column(DateTime, nullable=False)
    author = Column(String(50), nullable=False)
    author_data = Column(String(50), nullable=False)
    content = Column(String, nullable=False)
    group_link = Column(String(1000), nullable=False)
    reactions = Column(INTEGER, nullable=False)
    comments = Column(INTEGER, nullable=False)
    shares = Column(INTEGER, nullable=False)
    scrapping_date = Column(DateTime, nullable=False)

    links = relationship('Link', secondary=PostLink, 
                         back_populates='post',
                         cascade='all, delete-orphan')
    
    images = relationship('Image', secondary=PostImage, 
                          back_populates='post',
                          cascade='all, delete-orphan')

    def __init__(self, link, date, author, author_data, content, group_link, reactions, comments, shares, scrapping_date):
        self.link = link
        self.date = date
        self.author = author
        self.author_data = author_data
        self.content = content
        self.group_link = group_link
        self.reactions = reactions
        self.comments = comments
        self.shares = shares
        self.scrapping_date = scrapping_date

engine = create_engine("sqlite:///dataextraction.db")

Base.metadata.create_all(bind=engine)

session = sessionmaker(bind=engine)

session = session()

def get_session():
    return session

def commit_session(session):
    try:
        session.commit()
        print("Post added successfully.")
    except Exception as e:
        session.rollback()  # Rollback the changes on error
        print("Failed to add post to the database.")
        print(e)        

def close_session(session):
    session.close()

def insert_post(post, session):
    # Check if the post already exists in the database
    existing_post = session.query(Post).filter_by(link=post.link).first()

    if existing_post:
        # Update existing post
        existing_post.reactions = post.reactions
        existing_post.comments = post.comments
        existing_post.shares = post.shares
        existing_post.scrapping_date = post.scrapping_date
    else:
        # Create a new Post object if it doesn't exist
        new_post = Post(
            link=post.link,
            date=post.date,
            author=post.author,
            author_data=post.author_data,
            content=post.content,
            group_link=post.group_link,
            reactions=post.reactions,
            comments=post.comments,
            shares=post.shares,
            scrapping_date=post.scrapping_date
        )

        # Process images and links similar to before
        for image_link in post.images:
            image = session.query(Image).filter_by(link=image_link).first()
            if not image:
                image = Image(link=image_link)
                session.add(image)
            new_post.images.append(image)

        for external_link in post.links:
            link = session.query(Link).filter_by(link=external_link).first()
            if not link:
                link = Link(link=external_link)
                session.add(link)
            new_post.links.append(link)

        # Add the new Post object to the session if it's new
        session.add(new_post)

    # Commit the session to save the changes to the database
    session.commit()

post = Post(
    date=datetime.now(),
    content="Sample post content",
    author="Author Name",
    author_data="Author Bio",
    comments=10,
    shares=5,
    reactions=100,
    group_link="http://group-link.com",
    link="http://post-link.com",
    scrapping_date=datetime.now()
)

