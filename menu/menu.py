import time

#
# Renders an interactive menu from a tree specification
# A tree is a list of dicts. Each dict contains:
#  "result": this will be returned if the item is selected
#  "icon": 2d list of pixels to display. Arbitrary size.
#  "menu": (optional) another menu tree, which will be displayed if this entry is selected
#
# Use `action` to provide input (e.g. Action.OK). It will return
# True,result if the user selects a menu item.
# result is a list of every `result` object selected on the way
# through the menu (i.e. the finally selected menu item last in the list,
# preceded by its parent menu, ...)
# example return value:
# True, ["settings", "network", "ssid", "Luke I am your bother"]


class Action:
    OK = 0
    BACK = 1
    UP = 2
    DOWN = 3
    TIMEOUT = 4


class Menu:
    def __init__(self, tree):

        assert(self.is_valid_tree(tree))

        # Last element is the parent menu
        # Element before that is the parent parent menu, etc
        self.stack = []

        # The menu items we've OK'd to get to where we are
        self.selection = []

        # Currently active menu
        self.tree = tree

        # Currently selected index
        self.index = 0

        # Animation to show wide icons
        # Min X offset, Max X offset, current X offset, current direction
        self.animation = (0, 0, 0, 1)
        self.animation_ticks = time.ticks_ms()


        pass

    def is_valid_tree(self, tree):
        if type(tree) != list:
            print(f"A menu was found which is not a list: {tree}")
            return False
        
        for entry in tree:
            if type(entry) != dict:
                print(f"A menu entry was found which is not a dict: {tree}")
                return False

            if "result" not in entry:
                print(f"A menu entry is missing a result object: {tree}")
                return False

            if "icon" not in entry:
                print(f"A menu entry is missing an icon: {tree}")
                return False
            
            if type(entry["icon"]) != list:
                print(f"A menu entry has an icon which is not a list: {tree}")
                return False
            
            for row in entry["icon"]:
                if type(row) != list:
                    print(f"A menu entry has an icon which is not a list of lists: {tree}")
                    return False

                if not all([type(px) == int for px in row]):
                    print(f"A menu entry has an icon which is not a list of lists of int: {tree}")
                    return False

            
            if "menu" in entry:
                if not self.is_valid_tree(entry["menu"]):
                    return False
        return True

    def action(self, disp, action):
        before_entry = self.tree[self.index]

        if action == Action.UP:
            self.index -= 1
            self.index = self.index % len(self.tree)

        if action == Action.DOWN:
            self.index += 1
            self.index = self.index % len(self.tree)
        
        # Bounce the icon, if it's too large
        self.init_animation(self.tree[self.index]["icon"])
    
        if action == Action.BACK or action == Action.TIMEOUT:
            if self.stack == []:
                # Backed out of the top-level menu
                return True, None
    
            # Go back one step
            self.tree = self.stack[-1]
            self.stack = self.stack[:-1]
            self.selection = self.selection[:-1]
            self.index = 0

            after_entry = self.tree[self.index]

            # Animate the transition
            self._swap_icon(disp, before_entry["icon"], after_entry["icon"], -16, 1)

            # Bounce the icon if it's too large to fit
            self.init_animation(after_entry["icon"])

            return False, None
            
        if action == Action.OK:
            entry = self.tree[self.index]

            if "menu" in entry:
                # Move down the menu tree
                self.selection.append(entry["result"])
                self.stack.append(self.tree)
                self.tree = entry["menu"]
                self.index = 0

                after_entry = self.tree[self.index]

                # Animate!!
                self._swap_icon(disp, before_entry["icon"], after_entry["icon"], 16, -1)

                self.init_animation(after_entry["icon"])

                return False, None
            
            else:
                # Finally selected a menu entry!!
                return True, self.selection + [ entry["result"] ]
                
            
        # Not ready to end yet
        return False, None
    
    def _center_icon(self, icon):
        height = len(icon)
        width = max([len(row) for row in icon])

        x = max(0, (16-width)//2)
        y = max(0, (16-height)//2)

        return  x,y
    
    # direction is 1 for rightward, 1 for leftward
    # new_offset is -16 for left off-screen, 16 for right off-screen
    def _swap_icon(self, disp, cur_icon, new_icon, new_offset=-16, direction=1):
        x1, y1 = self._center_icon(cur_icon)
        x2, y2 = self._center_icon(new_icon)

        for step in range(16):
            disp.clear()
            self._draw_icon(disp, new_icon, x2+new_offset+direction*step, y2)
            self._draw_icon(disp, cur_icon,  x1+direction*step, y1)
            disp.flip()
            time.sleep(0.03)


    def _draw_icon(self, disp, icon, x, y):

        for dy in range(len(icon)):
            if y+dy < 0: continue
            if y+dy > 15: continue
            row = icon[dy]
            for dx in range(len(row)):
                if x+dx < 0: continue
                if x+dx > 15: continue
                disp.set(x+dx, y+dy, row[dx])

    def animate(self):

        now = time.ticks_ms()
        dt = time.ticks_diff(now, self.animation_ticks)

        min_x, max_x, x, direction = self.animation


        if x < min_x:
            if dt > 500:        # Hold at the edge for a bit
                x = min_x
                direction = 1
                self.animation_ticks = now
        elif x > max_x:
            if dt > 500:        # Hold at the edge for a bit
                x = max_x
                direction = -1
                self.animation_ticks = now
        else:
            if dt > 60:
                x += direction
                self.animation_ticks = now

        self.animation = (min_x, max_x, x, direction)
    
    def init_animation(self, icon):
        w = max(len(row) for row in icon)

        if w < 16:
            self.animation = (0, 0, 0, 1)      # No animation
        else:
            self.animation = (0, w-16, 0, 1)

        self.animation_ticks = time.ticks_ms()


    def draw(self, disp):
        entry = self.tree[self.index]

        
        
        min_x, max_x, x_offset, direction = self.animation

        disp.clear()

        x,y = self._center_icon(entry["icon"])
        
        if min_x == max_x:
            # Not animating
            self._draw_icon(disp, entry["icon"], x, y)

        else:
            # Animating
            self._draw_icon(disp, entry["icon"], -x_offset, y)
            self.animate()

        disp.flip()

        return