from App.database import db

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5 stars
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Review {self.rating} stars by User {self.user_id}>"

    def get_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "apartment_id": self.apartment_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "author": self.author.username  # Include username of the tenant
    }