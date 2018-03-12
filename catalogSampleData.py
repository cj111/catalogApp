from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

from models import Base, User, Category, Product

engine = create_engine('postgresql://catalog:password1@127.0.0.1:5432/catalogDB')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

session.execute("DELETE FROM \"user\"")
session.execute("DELETE FROM category")
session.execute("DELETE FROM product")
# Create dummy user
User1 = User(name="Jorge Test", email="jleandro.ceballos@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

User2 = User(name="Eva Test", email="Hello@World.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User2)
session.commit()

Category1 = Category(name="Soccer", user_id = 2)
session.add(Category1)
session.commit()

Category2 = Category(name="Basketball", user_id = 2)
session.add(Category2)
session.commit()

Product1 = Product(name="soccer ball", description="Adidas soccer ball, Size 5 regulation", 
					picture="https://cdn1.thehunt.com/app/public/system/note_images/8020734/note_view/4278d4de8169d370f00a1e550d6fa0ed.jpg",
					create_time = date.today(), category_id = 1, user_id = 2)
session.add(Product1)
session.commit()

Product2 = Product(name="cleats", description="Adidas cleats, for firm ground.", 
					picture="https://cdn3.volusion.com/tjyvc.unaha/v/vspfiles/photos/S74597-2.jpg",
					create_time = date.today(), category_id = 1, user_id = 2)
session.add(Product2)
session.commit()

Product3 = Product(name="Basketball ball", description="Spalding basketball, NBA approved", 
					picture="http://www.gamebasketballs.com/wp-content/uploads/spalding-velocity-350x350.jpg",
					create_time = date.today(), category_id = 2, user_id = 2)
session.add(Product3)
session.commit()

Product4 = Product(name="Basketball shoes", description="Adidas cleats, for frm ground.", 
					picture="https://www.kicksusa.com/media/catalog/product/cache/1/thumbnail/350x/602f0fa2c1f0d1ba5e241f914e856ff9/a/d/adidas_by3602_01.jpg",
					create_time = date.today(), category_id = 2, user_id = 2)
session.add(Product4)
session.commit()


print "added products!"
